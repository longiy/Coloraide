"""
Core operators for color picker functionality - Blender 5.0+
Samples the GPU framebuffer directly from modal() on MOUSEMOVE, using
fb.viewport_get() for bounds and absolute event.mouse_x/y coordinates
(clamping required for Vulkan) — same approach as color-picker-pro
(https://github.com/semagnum/color-picker-pro).
"""

import sys
import bpy
import gpu
import numpy as np
from bpy.types import Operator
from gpu_extras.batch import batch_for_shader
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_sync import is_updating
from ..COLORAIDE_colorspace import rgb_linear_to_srgb

# Vertex data for color preview rectangles
vertices = ((0, 0), (100, 0), (0, -100), (100, -100))
indices = ((0, 1, 2), (2, 1, 3), (0, 1, 1), (1, 2, 2), (2, 2, 3), (3, 0, 0))

try:
    fill_shader = gpu.shader.from_builtin('UNIFORM_COLOR')
except Exception as e:
    import logging
    logging.getLogger(__name__).warning(f'Failed to initialize gpu shader: {e}')


def draw_preview_boxes(op):
    """POST_PIXEL callback — draws mean/current colour swatches near the cursor."""
    m_x = op.x
    m_y = op.y
    length = op.sqrt_length + 5
    wm = bpy.context.window_manager

    mean_srgb = rgb_linear_to_srgb(tuple(wm.coloraide_picker.mean))
    fill_shader.uniform_float("color", tuple(list(mean_srgb) + [1.0]))
    verts = tuple((m_x + x + length, m_y + y - length) for x, y in vertices)
    batch_for_shader(fill_shader, 'TRIS', {"pos": verts}, indices=indices).draw(fill_shader)

    curr_srgb = rgb_linear_to_srgb(tuple(wm.coloraide_picker.current))
    fill_shader.uniform_float("color", tuple(list(curr_srgb) + [1.0]))
    verts2 = tuple((m_x + x + length + 100, m_y + y - length) for x, y in vertices)
    batch_for_shader(fill_shader, 'TRIS', {"pos": verts2}, indices=indices).draw(fill_shader)


# ---------------------------------------------------------------------------
# GPU framebuffer sampling — called directly from modal(), not a draw handler
# ---------------------------------------------------------------------------

def _gpu_read_colors(op, event):
    """
    Read the active framebuffer around the cursor and push pixel data to
    picker state. Uses fb.viewport_get() for bounds (already in the same
    physical-pixel, absolute-screen coordinate space as event.mouse_x/y),
    so this is correct under Retina/HiDPI and Windows display scaling
    without any manual coordinate conversion.
    """
    if is_updating('picker'):
        return

    fb = gpu.state.active_framebuffer_get()
    min_x, min_y, max_x, max_y = fb.viewport_get()

    sqrt_length = op.sqrt_length
    distance    = sqrt_length // 2
    mouse_x, mouse_y = event.mouse_x, event.mouse_y

    # Clamping is required for Vulkan.
    sx = min(max(mouse_x - distance, min_x), max_x - sqrt_length - 1)
    sy = min(max(mouse_y - distance, min_y), max_y - sqrt_length - 1)
    try:
        area_buf = fb.read_color(sx, sy, sqrt_length, sqrt_length, 3, 0, 'FLOAT')
    except ValueError:
        return

    # Framebuffer values are already scene-linear — no sRGB decode needed.
    channels_raw = np.array(area_buf.to_list()).reshape((sqrt_length * sqrt_length, 3))
    mean_linear  = tuple(np.mean(channels_raw, axis=0))

    px = min(max(mouse_x, min_x), max_x - 1)
    py = min(max(mouse_y, min_y), max_y - 1)
    try:
        px_buf = fb.read_color(px, py, 1, 1, 3, 0, 'FLOAT')
    except ValueError:
        return
    curr_linear = tuple(np.array(px_buf.to_list()).reshape(-1))

    wm = bpy.context.window_manager
    dot = np.sum(channels_raw, axis=1)
    wm.coloraide_picker.max    = tuple(channels_raw[np.argmax(dot)])
    wm.coloraide_picker.min    = tuple(channels_raw[np.argmin(dot)])
    wm.coloraide_picker.median = tuple(np.median(channels_raw, axis=0))

    wm.coloraide_picker.suppress_updates = True
    wm.coloraide_picker.mean    = mean_linear
    wm.coloraide_picker.current = curr_linear
    wm.coloraide_picker.suppress_updates = False
    sync_all(bpy.context, 'picker', mean_linear)


# ---------------------------------------------------------------------------
# Shared mixin
# ---------------------------------------------------------------------------

class _PickerHandlerMixin:
    """Shared draw-handler teardown for screen picker operators."""
    _draw_handler = None

    def _cleanup_handlers(self, context):
        context.window.cursor_modal_restore()
        space = getattr(bpy.types, self._handler_space_type, None)
        if space and self._draw_handler:
            space.draw_handler_remove(self._draw_handler, 'WINDOW')
            self._draw_handler = None


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class IMAGE_OT_screen_picker_quick(_PickerHandlerMixin, Operator):
    """Sample colors from screen — used for both 1×1 and custom-size buttons"""
    bl_idname = "image.screen_picker_quick"
    bl_label = "Screen Color Picker"
    bl_description = "Sample colors from screen"
    bl_options = {'REGISTER'}

    sqrt_length:    bpy.props.IntProperty(default=1)
    x:              bpy.props.IntProperty()
    y:              bpy.props.IntProperty()

    def cleanup(self, context):
        self._cleanup_handlers(context)

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'MOUSEMOVE', 'LEFTMOUSE'}:
            self.x = event.mouse_region_x
            self.y = event.mouse_region_y
            _gpu_read_colors(self, event)

        if event.type == 'LEFTMOUSE':
            self.cleanup(context)
            if hasattr(context.window_manager, 'coloraide_history'):
                context.window_manager.coloraide_history.add_color(
                    tuple(context.window_manager.coloraide_picker.mean))
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cleanup(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.x = event.mouse_region_x
        self.y = event.mouse_region_y
        _gpu_read_colors(self, event)
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')

        self._handler_space_type = context.space_data.__class__.__name__
        space = getattr(bpy.types, self._handler_space_type)
        self._draw_handler = space.draw_handler_add(
            draw_preview_boxes, (self,), 'WINDOW', 'POST_PIXEL')
        return {'RUNNING_MODAL'}


class IMAGE_OT_quickpick(_PickerHandlerMixin, Operator):
    """Quick color picker activated by hotkey"""
    bl_idname = "image.quickpick"
    bl_label = "Quick Color Picker"
    bl_description = "Press and hold to activate color picker, release to select color"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.StringProperty(default='DEFAULT')

    _key_pressed  = None
    sqrt_length:    bpy.props.IntProperty(default=3)
    x:              bpy.props.IntProperty()
    y:              bpy.props.IntProperty()

    def cleanup(self, context, add_to_history=True):
        self._cleanup_handlers(context)
        if add_to_history and hasattr(context.window_manager, 'coloraide_history'):
            context.window_manager.coloraide_history.add_color(
                tuple(context.window_manager.coloraide_picker.mean))

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == self._key_pressed and event.value == 'RELEASE':
            self.cleanup(context, add_to_history=True)
            return {'FINISHED'}

        elif event.type == 'MOUSEMOVE':
            if is_updating('picker'):
                return {'PASS_THROUGH'}
            self.sqrt_length = context.window_manager.coloraide_picker.custom_size
            self.x           = event.mouse_region_x
            self.y           = event.mouse_region_y
            _gpu_read_colors(self, event)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cleanup(context, add_to_history=False)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self._key_pressed = event.type
        self.sqrt_length   = context.window_manager.coloraide_picker.custom_size
        self.x             = event.mouse_region_x
        self.y             = event.mouse_region_y
        _gpu_read_colors(self, event)
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')

        self._handler_space_type = context.space_data.__class__.__name__
        space = getattr(bpy.types, self._handler_space_type)
        self._draw_handler = space.draw_handler_add(
            draw_preview_boxes, (self,), 'WINDOW', 'POST_PIXEL')
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(IMAGE_OT_screen_picker_quick)
    bpy.utils.register_class(IMAGE_OT_quickpick)

def unregister():
    bpy.utils.unregister_class(IMAGE_OT_quickpick)
    bpy.utils.unregister_class(IMAGE_OT_screen_picker_quick)
