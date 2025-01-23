"""
Core operators for color picker functionality.
"""

import bpy
import gpu
import numpy as np
from bpy.types import Operator
from gpu_extras.batch import batch_for_shader
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating, UpdateFlags

# Vertex data for color preview rectangles
vertices = ((0, 0), (100, 0), (0, -100), (100, -100))
indices = ((0, 1, 2), (2, 1, 3), (0, 1, 1), (1, 2, 2), (2, 2, 3), (3, 0, 0))

# Set up shaders based on Blender version
UNIFORM_COLOR = '2D_UNIFORM_COLOR' if bpy.app.version < (3, 4, 0) else 'UNIFORM_COLOR'
try:
    fill_shader = gpu.shader.from_builtin(UNIFORM_COLOR)
    edge_shader = gpu.shader.from_builtin(UNIFORM_COLOR)
except Exception as e:
    import logging
    log = logging.getLogger(__name__)
    log.warning('Failed to initialize gpu shader')

def draw_color_preview(op):
    """Draw color preview rectangles during picking"""
    m_x, m_y = op.x, op.y
    length = op.sqrt_length + 5
    
    # Draw mean color rectangle
    mean_color = tuple(list(bpy.context.window_manager.coloraide_picker.mean) + [1.0])
    fill_shader.uniform_float("color", mean_color)
    
    draw_verts_mean = tuple((m_x + x + length, m_y + y - length) for x,y in vertices)
    batch_mean = batch_for_shader(fill_shader, 'TRIS', {"pos": draw_verts_mean}, indices=indices)
    batch_mean.draw(fill_shader)
    
    # Draw current picked color rectangle
    current_color = tuple(list(bpy.context.window_manager.coloraide_picker.current) + [1.0])
    fill_shader.uniform_float("color", current_color)
    
    offset_x = 100  # Width + gap
    draw_verts_current = tuple((m_x + x + length + offset_x, m_y + y - length) for x,y in vertices)
    batch_current = batch_for_shader(fill_shader, 'TRIS', {"pos": draw_verts_current}, indices=indices)
    batch_current.draw(fill_shader)

class IMAGE_OT_screen_picker(Operator):
    """Sample colors from screen with custom size"""
    bl_idname = "image.screen_picker"
    bl_label = "Screen Color Picker"
    bl_description = "Sample colors from screen with adjustable area"
    bl_options = {'REGISTER'}
    
    sqrt_length: bpy.props.IntProperty()
    x: bpy.props.IntProperty()
    y: bpy.props.IntProperty()
    _handler = None
    
    def sample_colors(self, context, event):
        """Sample colors from screen and update properties"""
        if is_updating('picker'):
            return
            
        distance = self.sqrt_length // 2
        start_x = max(event.mouse_x - distance, 0)
        start_y = max(event.mouse_y - distance, 0)

        fb = gpu.state.active_framebuffer_get()
        
        # Sample area for mean color
        screen_buffer = fb.read_color(start_x, start_y, self.sqrt_length, self.sqrt_length, 3, 0, 'FLOAT')
        channels = np.array(screen_buffer.to_list()).reshape((self.sqrt_length * self.sqrt_length, 3))
        mean_color = np.mean(channels, axis=0)
        
        # Sample current pixel
        curr_buffer = fb.read_color(event.mouse_x, event.mouse_y, 1, 1, 3, 0, 'FLOAT')
        current_color = np.array(curr_buffer.to_list()).reshape(-1)
        
        # Update statistics
        dot = np.sum(channels, axis=1)
        max_ind = np.argmax(dot, axis=0)
        min_ind = np.argmin(dot, axis=0)
        
        # Update properties using sync system
        wm = context.window_manager
        wm.coloraide_picker.current = tuple(current_color)
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

class IMAGE_OT_quickpick(Operator):
    """Quick color picker activated by hotkey"""
    bl_idname = "image.quickpick"
    bl_label = "Quick Color Picker"
    bl_description = "Press and hold to activate color picker, release to select color"
    bl_options = {'REGISTER', 'UNDO'}
    
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
            
            # Sample colors
            screen_buffer = fb.read_color(start_x, start_y, self.sqrt_length, self.sqrt_length, 3, 0, 'FLOAT')
            channels = np.array(screen_buffer.to_list()).reshape((self.sqrt_length * self.sqrt_length, 3))
            mean_color = np.mean(channels, axis=0)
            
            curr_buffer = fb.read_color(event.mouse_x, event.mouse_y, 1, 1, 3, 0, 'FLOAT')
            current_color = np.array(curr_buffer.to_list()).reshape(-1)
            
            # Update statistics
            dot = np.sum(channels, axis=1)
            max_ind = np.argmax(dot, axis=0)
            min_ind = np.argmin(dot, axis=0)
            
            wm = context.window_manager
            wm.coloraide_picker.max = tuple(channels[max_ind])
            wm.coloraide_picker.min = tuple(channels[min_ind])
            wm.coloraide_picker.median = tuple(np.median(channels, axis=0))
            
            # Update picker values using sync system
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
    bpy.utils.register_class(IMAGE_OT_quickpick)

def unregister():
    bpy.utils.unregister_class(IMAGE_OT_quickpick)
    bpy.utils.unregister_class(IMAGE_OT_screen_picker)