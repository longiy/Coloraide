"""
Core operators for color picker functionality - Blender 5.0+

Platform strategy
-----------------
macOS  (Metal)  : CGWindowListCreateImage via CoreGraphics ctypes.
                  Requires Screen Recording permission in System Settings.
Windows (OpenGL/Vulkan) : GDI32 BitBlt via ctypes. No extra permissions.
Linux           : gpu.state.active_framebuffer_get() in a POST_VIEW draw
                  callback (GPU framebuffer is accessible on OpenGL/Vulkan).
"""

import sys
import bpy
import gpu
import numpy as np
from bpy.types import Operator
from gpu_extras.batch import batch_for_shader
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_sync import is_updating
from ..COLORAIDE_colorspace import rgb_linear_to_srgb, rgb_srgb_to_linear
from .CPICKER_screen import sample_at_cursor, is_native_capture_available

# Vertex data for color preview rectangles
vertices = ((0, 0), (100, 0), (0, -100), (100, -100))
indices = ((0, 1, 2), (2, 1, 3), (0, 1, 1), (1, 2, 2), (2, 2, 3), (3, 0, 0))

try:
    fill_shader = gpu.shader.from_builtin('UNIFORM_COLOR')
except Exception as e:
    import logging
    logging.getLogger(__name__).warning(f'Failed to initialize gpu shader: {e}')


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _apply_sample(context, channels_srgb, mean_srgb, curr_srgb):
    """Convert sampled sRGB values to scene-linear and push through sync."""
    if mean_srgb is None:
        return
    mean_linear = rgb_srgb_to_linear(tuple(mean_srgb))
    curr_linear = rgb_srgb_to_linear(tuple(curr_srgb))

    wm = context.window_manager
    if channels_srgb is not None and len(channels_srgb) > 0:
        channels_linear = np.array([rgb_srgb_to_linear(tuple(c)) for c in channels_srgb])
        dot = np.sum(channels_linear, axis=1)
        wm.coloraide_picker.max    = tuple(channels_linear[np.argmax(dot)])
        wm.coloraide_picker.min    = tuple(channels_linear[np.argmin(dot)])
        wm.coloraide_picker.median = tuple(np.median(channels_linear, axis=0))

    # sync_all skips picker.mean when source='picker' (anti-recursion guard),
    # so we must set mean explicitly here alongside current.
    wm.coloraide_picker.suppress_updates = True
    wm.coloraide_picker.mean    = tuple(mean_linear)
    wm.coloraide_picker.current = tuple(curr_linear)
    wm.coloraide_picker.suppress_updates = False
    sync_all(context, 'picker', tuple(mean_linear))


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
# Linux GPU framebuffer path (POST_VIEW draw callback)
# ---------------------------------------------------------------------------

def _gpu_read_colors(op):
    """
    POST_VIEW draw callback used on Linux.
    At this point the GPU framebuffer contains the rendered scene (OpenGL/Vulkan).
    Reads pixel data and pushes to picker state.
    """
    context = bpy.context
    region  = context.region
    if region.as_pointer() != op.invoke_region_ptr:
        return
    if is_updating('picker'):
        return

    fb   = gpu.state.active_framebuffer_get()
    fw   = region.width
    fh   = region.height
    dist = op.sqrt_length // 2
    mx   = op.mouse_region_x
    my   = op.mouse_region_y

    sx = max(0, min(mx - dist, fw - op.sqrt_length))
    sy = max(0, min(my - dist, fh - op.sqrt_length))
    sw = min(op.sqrt_length, fw - sx)
    sh = min(op.sqrt_length, fh - sy)
    if sw <= 0 or sh <= 0:
        return

    try:
        area_buf = fb.read_color(sx, sy, sw, sh, 3, 0, 'FLOAT')
    except ValueError:
        return

    channels_raw = np.array(area_buf.to_list()).reshape((sw * sh, 3))
    mean_raw     = np.mean(channels_raw, axis=0)
    mean_linear  = rgb_srgb_to_linear(tuple(mean_raw))

    px = max(0, min(mx, fw - 1))
    py = max(0, min(my, fh - 1))
    try:
        px_buf = fb.read_color(px, py, 1, 1, 3, 0, 'FLOAT')
    except ValueError:
        return
    curr_raw    = np.array(px_buf.to_list()).reshape(-1)
    curr_linear = rgb_srgb_to_linear(tuple(curr_raw))

    wm = context.window_manager
    channels_linear = np.array([rgb_srgb_to_linear(tuple(c)) for c in channels_raw])
    dot = np.sum(channels_linear, axis=1)
    wm.coloraide_picker.max    = tuple(channels_linear[np.argmax(dot)])
    wm.coloraide_picker.min    = tuple(channels_linear[np.argmin(dot)])
    wm.coloraide_picker.median = tuple(np.median(channels_linear, axis=0))

    wm.coloraide_picker.suppress_updates = True
    wm.coloraide_picker.mean    = tuple(mean_linear)
    wm.coloraide_picker.current = tuple(curr_linear)
    wm.coloraide_picker.suppress_updates = False
    sync_all(context, 'picker', tuple(mean_linear))


# ---------------------------------------------------------------------------
# Shared mixin
# ---------------------------------------------------------------------------

class _PickerHandlerMixin:
    """Shared draw-handler teardown for screen picker operators."""
    _draw_handler = None
    _read_handler = None

    def _cleanup_handlers(self, context):
        context.window.cursor_modal_restore()
        space = getattr(bpy.types, self._handler_space_type, None)
        if space:
            if self._draw_handler:
                space.draw_handler_remove(self._draw_handler, 'WINDOW')
                self._draw_handler = None
            if self._read_handler:
                space.draw_handler_remove(self._read_handler, 'WINDOW')
                self._read_handler = None


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
    mouse_region_x: bpy.props.IntProperty()
    mouse_region_y: bpy.props.IntProperty()

    invoke_region_ptr = 0

    def cleanup(self, context):
        self._cleanup_handlers(context)

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'MOUSEMOVE', 'LEFTMOUSE'}:
            self.x = event.mouse_region_x
            self.y = event.mouse_region_y
            self.mouse_region_x = event.mouse_region_x
            self.mouse_region_y = event.mouse_region_y
            if is_native_capture_available() and not is_updating('picker'):
                channels, mean_s, curr_s = sample_at_cursor(self.sqrt_length)
                _apply_sample(context, channels, mean_s, curr_s)

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
        self.mouse_region_x = event.mouse_region_x
        self.mouse_region_y = event.mouse_region_y
        self.invoke_region_ptr = context.region.as_pointer()
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')

        self._handler_space_type = context.space_data.__class__.__name__
        space = getattr(bpy.types, self._handler_space_type)
        self._draw_handler = space.draw_handler_add(
            draw_preview_boxes, (self,), 'WINDOW', 'POST_PIXEL')
        if not is_native_capture_available():
            self._read_handler = space.draw_handler_add(
                _gpu_read_colors, (self,), 'WINDOW', 'POST_VIEW')
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
    mouse_region_x: bpy.props.IntProperty()
    mouse_region_y: bpy.props.IntProperty()

    invoke_region_ptr = 0

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

        elif event.type in {'MOUSEMOVE'} or (event.type == self._key_pressed):
            if is_updating('picker'):
                return {'PASS_THROUGH'}
            self.sqrt_length   = context.window_manager.coloraide_picker.custom_size
            self.x             = event.mouse_region_x
            self.y             = event.mouse_region_y
            self.mouse_region_x = event.mouse_region_x
            self.mouse_region_y = event.mouse_region_y
            if is_native_capture_available():
                channels, mean_s, curr_s = sample_at_cursor(self.sqrt_length)
                _apply_sample(context, channels, mean_s, curr_s)
            # Linux: sampling happens in _gpu_read_colors draw callback

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cleanup(context, add_to_history=False)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self._key_pressed  = event.type
        self.sqrt_length   = context.window_manager.coloraide_picker.custom_size
        self.x             = event.mouse_region_x
        self.y             = event.mouse_region_y
        self.mouse_region_x = event.mouse_region_x
        self.mouse_region_y = event.mouse_region_y
        self.invoke_region_ptr = context.region.as_pointer()
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')

        self._handler_space_type = context.space_data.__class__.__name__
        space = getattr(bpy.types, self._handler_space_type)
        self._draw_handler = space.draw_handler_add(
            draw_preview_boxes, (self,), 'WINDOW', 'POST_PIXEL')
        if not is_native_capture_available():
            self._read_handler = space.draw_handler_add(
                _gpu_read_colors, (self,), 'WINDOW', 'POST_VIEW')
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(IMAGE_OT_screen_picker_quick)
    bpy.utils.register_class(IMAGE_OT_quickpick)

def unregister():
    bpy.utils.unregister_class(IMAGE_OT_quickpick)
    bpy.utils.unregister_class(IMAGE_OT_screen_picker_quick)
