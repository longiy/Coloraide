# COLORAIDE_monitor.py
import bpy
from bpy.types import Operator
from .COLORAIDE_brush_sync import sync_picker_from_brush, is_brush_updating
from .COLORAIDE_palette_bridge import is_palette_locked

class COLOR_OT_monitor(Operator):
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    old_color = None
    _timer = None
    
    def modal(self, context, event):
        try:
            if event.type != 'TIMER':
                return {'PASS_THROUGH'}
                
            # Skip if palette is handling updates
            if is_palette_locked():
                return {'PASS_THROUGH'}
                
            ts = context.tool_settings
            curr_color = None
            
            if context.mode == 'PAINT_GPENCIL' and ts.gpencil_paint.brush:
                curr_color = tuple(ts.gpencil_paint.brush.color)
            elif ts.image_paint and ts.image_paint.brush:
                curr_color = tuple(ts.image_paint.brush.color)
            
            if curr_color and (self.old_color is None or 
                any(abs(a - b) > 0.001 for a, b in zip(curr_color, self.old_color))):
                if not is_brush_updating():
                    sync_picker_from_brush(context, curr_color)
                self.old_color = curr_color
                
        except Exception as e:
            print(f"Color monitor error: {e}")
            
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
        
    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)