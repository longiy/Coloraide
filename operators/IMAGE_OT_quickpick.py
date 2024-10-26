import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import numpy as np

# Reuse the vertex and shader setup code
vertices = ((0, 0), (100, 0),
            (0, -100), (100, -100))
indices = ((0, 1, 2), (2, 1, 3), (0, 1, 1), (1, 2, 2), (2, 2, 3), (3, 0, 0))

UNIFORM_COLOR = '2D_UNIFORM_COLOR' if bpy.app.version < (3, 4, 0) else 'UNIFORM_COLOR'
try:
    fill_shader = gpu.shader.from_builtin(UNIFORM_COLOR)
    edge_shader = gpu.shader.from_builtin(UNIFORM_COLOR)
except SystemError as e:
    import logging
    log = logging.getLogger(__name__)
    log.warn('Failed to initialize gpu shader, draw will not work as expected')

def draw(operator):
    m_x, m_y = operator.x, operator.y
    length = operator.sqrt_length + 5
    
    # Draw mean color rectangle
    mean_color = tuple(list(bpy.context.window_manager.picker_mean) + [1.0])
    fill_shader.uniform_float("color", mean_color)

    # Original vertices for mean color
    draw_verts_mean = tuple((m_x + x + length, m_y + y - length) for x,y in vertices)
    batch_mean = batch_for_shader(fill_shader, 'TRIS', {"pos": draw_verts_mean}, indices=indices)
    batch_mean.draw(fill_shader)

    # Draw current picked color rectangle (offset to the right)
    current_color = tuple(list(operator.curr_color) + [1.0])
    fill_shader.uniform_float("color", current_color)

    # New vertices for current color (offset by rectangle width + small gap)
    offset_x = 100  # 100 (rectangle width) + 10 (gap)
    draw_verts_current = tuple((m_x + x + length + offset_x, m_y + y - length) for x,y in vertices)
    batch_current = batch_for_shader(fill_shader, 'TRIS', {"pos": draw_verts_current}, indices=indices)
    batch_current.draw(fill_shader)

def update_color_pickers(color):
    ts = bpy.context.tool_settings
    
    # Update Grease Pencil brush color
    if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
        ts.gpencil_paint.brush.color = color[:3]  # Use only RGB values
    
    # Update Texture Paint brush color
    if hasattr(ts, 'image_paint') and ts.image_paint.brush:
        # Update the brush color
        ts.image_paint.brush.color = color[:3]
        
        # Update the unified color settings if they're being used
        if ts.unified_paint_settings.use_unified_color:
            ts.unified_paint_settings.color = color[:3]

class IMAGE_OT_quickpick(bpy.types.Operator):
    bl_idname = "wm.quickpick_operator"
    bl_label = "Quick Color Picker"
    bl_description = "Press and hold to activate color picker, release to select color"
    bl_options = {'REGISTER', 'UNDO'}

    # Instead of checking specifically for backslash, we'll make it work with any key
    _key_pressed = None
    
    sqrt_length: bpy.props.IntProperty(default=3)
    x: bpy.props.IntProperty()
    y: bpy.props.IntProperty()
    curr_color: bpy.props.FloatVectorProperty(size=3)
    _handler = None

    def modal(self, context, event):
        context.area.tag_redraw()
        wm = context.window_manager

        if event.type == self._key_pressed and event.value == 'RELEASE':
            # Clean up and finish on key release
            context.window.cursor_modal_restore()
            if self._handler:
                space = getattr(bpy.types, self.space_type)
                space.draw_handler_remove(self._handler, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'MOUSEMOVE'} or (event.type == self._key_pressed):
            # Update color picking
            self.sqrt_length = wm.custom_size
            distance = self.sqrt_length // 2
            start_x = max(event.mouse_x - distance, 0)
            start_y = max(event.mouse_y - distance, 0)

            self.x = event.mouse_region_x
            self.y = event.mouse_region_y

            fb = gpu.state.active_framebuffer_get()
            screen_buffer = fb.read_color(start_x, start_y, self.sqrt_length, self.sqrt_length, 3, 0, 'FLOAT')
            channels = np.array(screen_buffer.to_list()).reshape((self.sqrt_length * self.sqrt_length, 3))

            curr_picker_buffer = fb.read_color(event.mouse_x, event.mouse_y, 1, 1, 3, 0, 'FLOAT')
            self.curr_color = np.array(curr_picker_buffer.to_list()).reshape(-1)

            dot = np.sum(channels, axis=1)
            max_ind = np.argmax(dot, axis=0)
            min_ind = np.argmin(dot, axis=0)

            wm.picker_mean = tuple(np.mean(channels, axis=0))
            wm.picker_max = tuple(channels[max_ind])
            wm.picker_min = tuple(channels[min_ind])
            wm.picker_median = tuple(np.median(channels, axis=0))

            update_color_pickers(wm.picker_mean)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # Cancel operation
            context.window.cursor_modal_restore()
            if self._handler:
                space = getattr(bpy.types, self.space_type)
                space.draw_handler_remove(self._handler, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self._key_pressed = event.type  # Store which key was used to invoke the operator
        wm = context.window_manager
        
        # Store initial values
        if not hasattr(wm, 'picker_mean'):
            wm.picker_mean = (0.0, 0.0, 0.0)
            wm.picker_median = (0.0, 0.0, 0.0)
            wm.picker_max = (0.0, 0.0, 0.0)
            wm.picker_min = (0.0, 0.0, 0.0)

        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')
        
        self.space_type = context.space_data.__class__.__name__
        space = getattr(bpy.types, self.space_type)
        self._handler = space.draw_handler_add(draw, (self,), 'WINDOW', 'POST_PIXEL')
        
        return {'RUNNING_MODAL'}

# Consolidated keymap management
addon_keymaps = []

def register_keymaps():
    # Register keymaps for all relevant areas
    wm = bpy.context.window_manager

    # kc = wm.keyconfigs.addon

    # if kc:
    #     # 3D View keymap
    #     km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    #     kmi = km.keymap_items.new("wm.quickpick_operator", "BACK_SLASH", "PRESS")
    #     addon_keymaps.append((km, kmi))

    #     # Image Editor keymap
    #     km = kc.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
    #     kmi = km.keymap_items.new("wm.quickpick_operator", "BACK_SLASH", "PRESS")
    #     addon_keymaps.append((km, kmi))

    #     # Clip Editor keymap
    #     km = kc.keymaps.new(name='Clip', space_type='CLIP_EDITOR')
    #     kmi = km.keymap_items.new("wm.quickpick_operator", "BACK_SLASH", "PRESS")
    #     addon_keymaps.append((km, kmi))

# def unregister_keymaps():
#     # Remove all keymaps
#     for km, kmi in addon_keymaps:
#         km.keymap_items.remove(kmi)
#     addon_keymaps.clear()

def register():
    bpy.utils.register_class(IMAGE_OT_quickpick)
    register_keymaps()

def unregister():
    unregister_keymaps()
    bpy.utils.unregister_class(IMAGE_OT_quickpick)

if __name__ == "__main__":
    register()