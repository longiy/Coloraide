"""
Core operators for color picker functionality.
Updated for Blender 4.3+ with optimized GPU operations.
"""

import bpy
import gpu
import numpy as np
from bpy.types import Operator
from gpu_extras.batch import batch_for_shader
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating

# Original working vertex data for color preview rectangles
vertices = ((0, 0), (100, 0), (0, -100), (100, -100))
indices = ((0, 1, 2), (2, 1, 3), (0, 1, 1), (1, 2, 2), (2, 2, 3), (3, 0, 0))

# Initialize shaders 
preview_shader = gpu.shader.from_builtin('UNIFORM_COLOR')

def create_preview_batch(x: float, y: float, length: float):
    """Create a single batch for both preview rectangles"""
    transformed_verts = []
    for vx, vy in preview_vertices:
        transformed_verts.append((x + vx + length, y + vy - length))
    
    return batch_for_shader(
        preview_shader, 'TRIS',
        {"pos": transformed_verts},
        indices=preview_indices
    )

def draw_color_preview(op):
    """Draw color preview rectangles during picking"""
    m_x, m_y = op.x, op.y
    length = op.sqrt_length + 5
    
    # Draw mean color rectangle
    mean_color = tuple(list(bpy.context.window_manager.coloraide_picker.mean) + [1.0])
    preview_shader.uniform_float("color", mean_color)
    
    draw_verts_mean = tuple((m_x + x + length, m_y + y - length) for x,y in vertices)
    batch_mean = batch_for_shader(preview_shader, 'TRIS', {"pos": draw_verts_mean}, indices=indices)
    batch_mean.draw(preview_shader)
    
    # Draw current picked color rectangle
    current_color = tuple(list(bpy.context.window_manager.coloraide_picker.current) + [1.0])
    preview_shader.uniform_float("color", current_color)
    
    offset_x = 100  # Width + gap
    draw_verts_current = tuple((m_x + x + length + offset_x, m_y + y - length) for x,y in vertices)
    batch_current = batch_for_shader(preview_shader, 'TRIS', {"pos": draw_verts_current}, indices=indices)
    batch_current.draw(preview_shader)

def sample_screen_colors(context, event, sqrt_length: int):
    """Optimized screen color sampling"""
    distance = sqrt_length // 2
    start_x = max(event.mouse_x - distance, 0)
    start_y = max(event.mouse_y - distance, 0)

    fb = gpu.state.active_framebuffer_get()
    
    # Sample area in a single read operation
    screen_buffer = fb.read_color(
        start_x, start_y,
        sqrt_length, sqrt_length,
        3, 0, 'FLOAT'
    )
    
    # Efficient numpy operations
    pixels = np.array(screen_buffer.to_list(), dtype=np.float32)
    pixels = pixels.reshape(-1, 3)
    
    # Calculate all statistics in one pass
    mean_color = np.mean(pixels, axis=0)
    median_color = np.median(pixels, axis=0)
    min_color = np.min(pixels, axis=0)
    max_color = np.max(pixels, axis=0)
    
    # Get current pixel color
    current_buffer = fb.read_color(
        event.mouse_x, event.mouse_y,
        1, 1, 3, 0, 'FLOAT'
    )
    current_color = np.array(current_buffer.to_list(), dtype=np.float32).reshape(3)
    
    return {
        'mean': tuple(mean_color),
        'current': tuple(current_color),
        'median': tuple(median_color),
        'min': tuple(min_color),
        'max': tuple(max_color)
    }

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
        if is_updating('picker'):
            return
        
        colors = sample_screen_colors(context, event, self.sqrt_length)
        
        wm = context.window_manager
        wm.coloraide_picker.current = colors['current']
        wm.coloraide_picker.median = colors['median']
        wm.coloraide_picker.min = colors['min']
        wm.coloraide_picker.max = colors['max']
        sync_all(context, 'picker', colors['mean'])
    
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
            self.x = event.mouse_region_x
            self.y = event.mouse_region_y
            
            # Use optimized sampling function
            colors = sample_screen_colors(context, event, self.sqrt_length)
            
            wm = context.window_manager
            wm.coloraide_picker.current = colors['current']
            wm.coloraide_picker.median = colors['median']
            wm.coloraide_picker.min = colors['min']
            wm.coloraide_picker.max = colors['max']
            sync_all(context, 'picker', colors['mean'])
        
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