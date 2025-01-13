"""
Copyright (C) 2023 Spencer Magnusson
semagnum@gmail.com
Created by Spencer Magnusson
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import numpy as np

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
    current_color = tuple(list(bpy.context.window_manager.picker_current) + [1.0])
    fill_shader.uniform_float("color", current_color)

    # New vertices for current color (offset by rectangle width + small gap)
    offset_x = 100  # 100 (rectangle width) + 10 (gap)
    draw_verts_current = tuple((m_x + x + length + offset_x, m_y + y - length) for x,y in vertices)
    batch_current = batch_for_shader(fill_shader, 'TRIS', {"pos": draw_verts_current}, indices=indices)
    batch_current.draw(fill_shader)

def update_color_history(color):
    wm = bpy.context.window_manager
    history = wm.picker_history
    
    # Check if color already exists in history
    for item in history:
        if (abs(item.color[0] - color[0]) < 0.001 and 
            abs(item.color[1] - color[1]) < 0.001 and 
            abs(item.color[2] - color[2]) < 0.001):
            return
    
    # Remove oldest color if we've reached the size limit
    if len(history) >= wm.history_size:
        history.remove(len(history) - 1)  # Remove the last item instead of first
    
    # Add new color at the beginning
    new_color = history.add()
    new_color.color = color
    
    # Move the new color to the start by shifting all items
    for i in range(len(history) - 1, 0, -1):
        history.move(i, i - 1)

def update_color_pickers(color, save_to_history=False):
    wm = bpy.context.window_manager
    ts = bpy.context.tool_settings
    
    # Update wheel color
    wm["wheel_color"] = (*color[:3], 1.0)  # Add alpha channel
    
    # Update Grease Pencil brush color
    if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
        ts.gpencil_paint.brush.color = color[:3]
    
    # Update Texture Paint brush color
    if hasattr(ts, 'image_paint') and ts.image_paint.brush:
        ts.image_paint.brush.color = color[:3]
        if ts.unified_paint_settings.use_unified_color:
            ts.unified_paint_settings.color = color[:3]
    
    # Update color history only when save_to_history is True
    if save_to_history:
        update_color_history(color[:3])

class IMAGE_OT_screen_picker(bpy.types.Operator):
    bl_idname = 'image.screen_picker'
    bl_label = 'Screen Picker'
    bl_description = 'Extract color information from multiple adjacent pixels'
    bl_options = {'REGISTER'}

    # square root of number of pixels taken into account
    sqrt_length: bpy.props.IntProperty()
    x: bpy.props.IntProperty()
    y: bpy.props.IntProperty()
    _handler = None

    def modal(self, context, event):
        context.area.tag_redraw()
        wm = context.window_manager

        if event.type in {'MOUSEMOVE', 'LEFTMOUSE'}:
            distance = self.sqrt_length // 2
            
            # Calculate start positions for the sample area
            start_x = max(event.mouse_x - distance, 0)
            start_y = max(event.mouse_y - distance, 0)

            self.x = event.mouse_region_x
            self.y = event.mouse_region_y

            fb = gpu.state.active_framebuffer_get()
            
            # Get the area sample for mean color
            screen_buffer = fb.read_color(start_x, start_y, self.sqrt_length, self.sqrt_length, 3, 0, 'FLOAT')
            channels = np.array(screen_buffer.to_list()).reshape((self.sqrt_length * self.sqrt_length, 3))

            # Get current pixel color (1x1 sample)
            curr_picker_buffer = fb.read_color(event.mouse_x, event.mouse_y, 1, 1, 3, 0, 'FLOAT')
            current_color = np.array(curr_picker_buffer.to_list()).reshape(-1)

            # Calculate mean color
            mean_color = np.mean(channels, axis=0)
            
            # Update window manager properties
            wm.picker_mean = tuple(mean_color)
            wm.picker_current = tuple(current_color)

            dot = np.sum(channels, axis=1)
            max_ind = np.argmax(dot, axis=0)
            min_ind = np.argmin(dot, axis=0)

            wm.picker_max = tuple(channels[max_ind])
            wm.picker_min = tuple(channels[min_ind])
            wm.picker_median = tuple(np.median(channels, axis=0))

            # Update tools with mean color
            update_color_pickers(mean_color)

        if event.type == 'LEFTMOUSE':
            # Save to history when finishing the pick
            update_color_pickers(wm.picker_mean, save_to_history=True)
            context.window.cursor_modal_restore()
            if self._handler:
                space = getattr(bpy.types, self.space_type)
                space.draw_handler_remove(self._handler, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # Cancel without saving to history
            wm.picker_mean = self.prev_mean
            wm.picker_current = self.prev_current
            wm.picker_median = self.prev_median
            wm.picker_max = self.prev_max
            wm.picker_min = self.prev_min
            context.window.cursor_modal_restore()
            if self._handler:
                space = getattr(bpy.types, self.space_type)
                space.draw_handler_remove(self._handler, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        
        # Store previous values for cancellation
        self.prev_mean = tuple(wm.picker_mean)
        self.prev_current = tuple(wm.picker_current)
        self.prev_median = tuple(wm.picker_median)
        self.prev_max = tuple(wm.picker_max)
        self.prev_min = tuple(wm.picker_min)
        
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')

        self.space_type = context.space_data.__class__.__name__
        space = getattr(bpy.types, self.space_type)
        self._handler = space.draw_handler_add(draw, (self,), 'WINDOW', 'POST_PIXEL')

        return {'RUNNING_MODAL'}