"""
Monitors brush color changes and syncs with Coloraide.
"""
import bpy

class COLOR_OT_monitor(bpy.types.Operator):
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    old_color = None
    _is_running = False
    
    def modal(self, context, event):
        try:
            # Get current brush color
            ts = context.tool_settings
            curr_color = None
            
            if context.mode == 'PAINT_GPENCIL' and ts.gpencil_paint.brush:
                curr_color = tuple(ts.gpencil_paint.brush.color)
            elif ts.image_paint and ts.image_paint.brush:
                curr_color = tuple(ts.image_paint.brush.color)
            
            # Only update and print if color actually changed
            if curr_color != self.old_color:
                self.old_color = curr_color
                if curr_color is not None:
                    context.window_manager.coloraide_picker.mean = curr_color
                    print(f"Color changed to: {curr_color}")  # Only prints on actual changes
            
        except Exception as e:
            print(f"Color monitor error: {e}")
            
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}