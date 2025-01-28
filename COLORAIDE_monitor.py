# COLORAIDE_monitor.py
import bpy
from bpy.types import Operator
from .COLORAIDE_brush_sync import sync_picker_from_brush, is_brush_updating

class COLOR_OT_monitor(Operator):
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    old_color = None
    
    def modal(self, context, event):
        try:
            ts = context.tool_settings
            curr_color = None
            
            # Handle Grease Pencil paint and vertex paint modes (4.3+ API)
            if (context.mode in {'PAINT_GREASE_PENCIL', 'VERTEX_GREASE_PENCIL'} and 
                context.active_object and 
                context.active_object.type == 'GREASEPENCIL'):
                if ts.gpencil_paint and ts.gpencil_paint.brush:
                    curr_color = tuple(ts.gpencil_paint.brush.color)
                    # Also check unified settings
                    if ts.unified_paint_settings.use_unified_color:
                        unified_color = tuple(ts.unified_paint_settings.color)
                        # Use unified color if it differs from brush color
                        if unified_color != curr_color:
                            curr_color = unified_color
            
            # Handle Image Paint mode
            elif ts.image_paint and ts.image_paint.brush:
                if ts.unified_paint_settings.use_unified_color:
                    curr_color = tuple(ts.unified_paint_settings.color)
                else:
                    curr_color = tuple(ts.image_paint.brush.color)
            
            if curr_color != self.old_color and curr_color is not None:
                if not is_brush_updating():
                    sync_picker_from_brush(context, curr_color)
                self.old_color = curr_color
                
        except Exception as e:
            print(f"Color monitor error: {e}")
            
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}