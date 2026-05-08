"""
Core operators for color picker functionality - Blender 5.0+
Framebuffer reading returns scene linear colors.
"""

import bpy
import gpu
import numpy as np
from bpy.types import Operator
from gpu_extras.batch import batch_for_shader
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_sync import is_updating
from ..COLORAIDE_colorspace import srgb_to_linear, rgb_linear_to_srgb, rgb_srgb_to_linear

def diagnose_framebuffer_color(raw_color):
    """
    Diagnostic to determine if framebuffer returns sRGB or linear.
    Tests with a known middle gray value.
    """
    print(f"\n=== COLOR DIAGNOSTIC ===")
    print(f"Blender version: {bpy.app.version}")
    print(f"Raw framebuffer value: {raw_color}")
    
    # If framebuffer is linear, 0.5 should be 0.5
    # If framebuffer is sRGB, 0.5 needs conversion to ~0.21 linear
    as_linear = srgb_to_linear(raw_color[0])
    print(f"If treating as sRGB→linear: {as_linear:.4f}")
    print(f"========================\n")
    
    return raw_color

# Vertex data for color preview rectangles
vertices = ((0, 0), (100, 0), (0, -100), (100, -100))
indices = ((0, 1, 2), (2, 1, 3), (0, 1, 1), (1, 2, 2), (2, 2, 3), (3, 0, 0))

# Set up shaders
UNIFORM_COLOR = 'UNIFORM_COLOR'
try:
    fill_shader = gpu.shader.from_builtin(UNIFORM_COLOR)
    edge_shader = gpu.shader.from_builtin(UNIFORM_COLOR)
except Exception as e:
    import logging
    log = logging.getLogger(__name__)
    log.warning('Failed to initialize gpu shader')



def draw_color_preview(op):
    """
    Draw color preview rectangles during picking.
    Colors are stored in scene linear, but GPU shader needs sRGB for display.
    """
    m_x, m_y = op.x, op.y
    length = op.sqrt_length + 5
    
    # Get mean color (scene linear) and convert to sRGB for display
    mean_linear = tuple(bpy.context.window_manager.coloraide_picker.mean)
    mean_srgb = rgb_linear_to_srgb(mean_linear)
    mean_color = tuple(list(mean_srgb) + [1.0])
    fill_shader.uniform_float("color", mean_color)
    
    draw_verts_mean = tuple((m_x + x + length, m_y + y - length) for x,y in vertices)
    batch_mean = batch_for_shader(fill_shader, 'TRIS', {"pos": draw_verts_mean}, indices=indices)
    batch_mean.draw(fill_shader)
    
    # Get current color (scene linear) and convert to sRGB for display
    current_linear = tuple(bpy.context.window_manager.coloraide_picker.current)
    current_srgb = rgb_linear_to_srgb(current_linear)
    current_color = tuple(list(current_srgb) + [1.0])
    fill_shader.uniform_float("color", current_color)
    
    offset_x = 100  # Width + gap
    draw_verts_current = tuple((m_x + x + length + offset_x, m_y + y - length) for x,y in vertices)
    batch_current = batch_for_shader(fill_shader, 'TRIS', {"pos": draw_verts_current}, indices=indices)
    batch_current.draw(fill_shader)
    batch_current.draw(fill_shader)

class IMAGE_OT_screen_picker(Operator):
    """Sample colors from screen with custom size"""
    bl_idname = "image.screen_picker"
    bl_label = "Screen Color Picker"
    bl_description = "Sample colors from screen 1x1 pixel area"
    bl_options = {'REGISTER'}
    
    sqrt_length: bpy.props.IntProperty()
    x: bpy.props.IntProperty()
    y: bpy.props.IntProperty()
    _handler = None
    
    def sample_colors(self, context, event):
        """
        Sample colors from framebuffer.
        
        NOTE: In Blender 5.0+, framebuffer.read_color() with format='FLOAT'
        returns colors in scene linear color space, not sRGB.
        This is the correct behavior for Blender's color management.
        """
        if is_updating('picker'):
            return
                
        distance = self.sqrt_length // 2
        start_x = max(event.mouse_x - distance, 0)
        start_y = max(event.mouse_y - distance, 0)

        fb = gpu.state.active_framebuffer_get()
        
        screen_buffer = fb.read_color(start_x, start_y, self.sqrt_length, self.sqrt_length, 3, 0, 'FLOAT')
        channels = np.array(screen_buffer.to_list()).reshape((self.sqrt_length * self.sqrt_length, 3))
        mean_color_srgb = np.mean(channels, axis=0)
        # Convert sRGB → scene linear (framebuffer returns sRGB in Blender 5.1.0)
        mean_color = rgb_srgb_to_linear(tuple(mean_color_srgb))

        # Sample single pixel for current color (also sRGB, needs conversion)
        curr_buffer = fb.read_color(event.mouse_x, event.mouse_y, 1, 1, 3, 0, 'FLOAT')
        current_color_srgb = np.array(curr_buffer.to_list()).reshape(-1)
        # Convert sRGB → scene linear
        current_color = rgb_srgb_to_linear(tuple(current_color_srgb))
        
        wm = context.window_manager
        # Update current color directly without sync (scene linear)
        wm.coloraide_picker.suppress_updates = True
        wm.coloraide_picker.current = tuple(current_color)
        wm.coloraide_picker.suppress_updates = False
        
        # Sync mean color (already scene linear)
        sync_all(context, 'picker', tuple(mean_color))
    
    def cleanup(self, context):
        """Clean up handlers and restore cursor"""
        context.window.cursor_modal_restore()
        if self._handler:
            space = getattr(bpy.types, self.space_type)
            space.draw_handler_remove(self._handler, 'WINDOW')
            self._handler = None
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type in {'MOUSEMOVE', 'LEFTMOUSE'}:
            self.sample_colors(context, event)
        
        if event.type == 'LEFTMOUSE':
            self.cleanup(context)
            
            # Add to history if available
            if hasattr(context.window_manager, 'coloraide_history'):
                context.window_manager.coloraide_history.add_color(
                    tuple(context.window_manager.coloraide_picker.mean)
                )
            return {'FINISHED'}
            
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cleanup(context)
            return {'CANCELLED'}
            
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')
        
        self.space_type = context.space_data.__class__.__name__
        space = getattr(bpy.types, self.space_type)
        self._handler = space.draw_handler_add(draw_color_preview, (self,), 'WINDOW', 'POST_PIXEL')
        
        return {'RUNNING_MODAL'}

class IMAGE_OT_screen_picker_quick(IMAGE_OT_screen_picker):
    """Sample colors with the custom size picker"""
    bl_idname = "image.screen_picker_quick"
    bl_label = "Custom Size Color Picker"
    bl_description = "Sample colors from screen custom pixel area"
    bl_options = {'REGISTER'}

class IMAGE_OT_quickpick(Operator):
    """Quick color picker activated by hotkey"""
    bl_idname = "image.quickpick"
    bl_label = "Quick Color Picker"
    bl_description = "Press and hold to activate color picker, release to select color"
    bl_options = {'REGISTER', 'UNDO'}
    
    mode: bpy.props.StringProperty(default='DEFAULT')
    
    _key_pressed = None
    sqrt_length: bpy.props.IntProperty(default=3)
    x: bpy.props.IntProperty()
    y: bpy.props.IntProperty()
    _handler = None
    
    def cleanup(self, context, add_to_history=True):
        """Clean up handlers and optionally add to history"""
        context.window.cursor_modal_restore()
        if self._handler:
            space = getattr(bpy.types, self.space_type)
            space.draw_handler_remove(self._handler, 'WINDOW')
            self._handler = None
        
        if add_to_history and hasattr(context.window_manager, 'coloraide_history'):
            context.window_manager.coloraide_history.add_color(
                tuple(context.window_manager.coloraide_picker.mean)
            )
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == self._key_pressed and event.value == 'RELEASE':
            self.cleanup(context, add_to_history=True)
            return {'FINISHED'}
        
        elif event.type in {'MOUSEMOVE'} or (event.type == self._key_pressed):
            if is_updating('picker'):
                return {'PASS_THROUGH'}
                
            # Use custom size from picker properties
            self.sqrt_length = context.window_manager.coloraide_picker.custom_size
            distance = self.sqrt_length // 2
            start_x = max(event.mouse_x - distance, 0)
            start_y = max(event.mouse_y - distance, 0)
            
            self.x = event.mouse_region_x
            self.y = event.mouse_region_y
            
            fb = gpu.state.active_framebuffer_get()

            # Sample colors (framebuffer returns sRGB, need conversion)
            screen_buffer = fb.read_color(start_x, start_y, self.sqrt_length, self.sqrt_length, 3, 0, 'FLOAT')
            channels_srgb = np.array(screen_buffer.to_list()).reshape((self.sqrt_length * self.sqrt_length, 3))
            mean_color_srgb = np.mean(channels_srgb, axis=0)
            # Convert sRGB → scene linear
            mean_color = rgb_srgb_to_linear(tuple(mean_color_srgb))

            curr_buffer = fb.read_color(event.mouse_x, event.mouse_y, 1, 1, 3, 0, 'FLOAT')
            current_color_srgb = np.array(curr_buffer.to_list()).reshape(-1)
            # Convert sRGB → scene linear
            current_color = rgb_srgb_to_linear(tuple(current_color_srgb))

            # Convert all sampled colors to scene linear for statistics
            channels = np.array([rgb_srgb_to_linear(tuple(c)) for c in channels_srgb])

            # Update statistics (now in scene linear)
            dot = np.sum(channels, axis=1)
            max_ind = np.argmax(dot, axis=0)
            min_ind = np.argmin(dot, axis=0)
            
            wm = context.window_manager
            wm.coloraide_picker.max = tuple(channels[max_ind])
            wm.coloraide_picker.min = tuple(channels[min_ind])
            wm.coloraide_picker.median = tuple(np.median(channels, axis=0))
            
            # Update picker values using sync system (scene linear)
            wm.coloraide_picker.current = tuple(current_color)
            sync_all(context, 'picker', tuple(mean_color))
        
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cleanup(context, add_to_history=False)
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        self._key_pressed = event.type
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')
        
        self.space_type = context.space_data.__class__.__name__
        space = getattr(bpy.types, self.space_type)
        self._handler = space.draw_handler_add(draw_color_preview, (self,), 'WINDOW', 'POST_PIXEL')
        
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(IMAGE_OT_screen_picker)
    bpy.utils.register_class(IMAGE_OT_screen_picker_quick)
    bpy.utils.register_class(IMAGE_OT_quickpick)

def unregister():
    bpy.utils.unregister_class(IMAGE_OT_quickpick)
    bpy.utils.unregister_class(IMAGE_OT_screen_picker_quick)
    bpy.utils.unregister_class(IMAGE_OT_screen_picker)
