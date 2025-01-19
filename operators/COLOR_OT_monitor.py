import bpy

from ..properties import is_update_in_progress, sync_picker_from_brush

class COLOR_OT_monitor(bpy.types.Operator):
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    old_color = None
    
    def modal(self, context, event):
        try:
            # Get current brush color
            ts = context.tool_settings
            curr_color = None
            
            if context.mode == 'PAINT_GPENCIL' and ts.gpencil_paint.brush:
                curr_color = tuple(ts.gpencil_paint.brush.color)
            elif ts.image_paint and ts.image_paint.brush:
                curr_color = tuple(ts.image_paint.brush.color)
            
            # Only sync if color changed and no internal updates are happening
            if curr_color != self.old_color and curr_color is not None:
                if not is_update_in_progress():
                    sync_picker_from_brush(context, curr_color)
                self.old_color = curr_color
            
        except Exception as e:
            print(f"Color monitor error: {e}")
            
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}