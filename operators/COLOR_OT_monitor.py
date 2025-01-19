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
        if not self._is_running:
            print("=== Color Monitor Started ===")
            self._is_running = True
        
        try:
            # Get current brush color
            ts = context.tool_settings
            curr_color = None
            
            if context.mode == 'PAINT_GPENCIL' and ts.gpencil_paint.brush:
                curr_color = tuple(ts.gpencil_paint.brush.color)
                print(f"Current GP brush color: {curr_color}")
            elif ts.image_paint and ts.image_paint.brush:
                curr_color = tuple(ts.image_paint.brush.color)
                print(f"Current image brush color: {curr_color}")
            
            # Check for color change without event filtering
            if curr_color != self.old_color:
                print("\n=== Color Change Detected ===")
                print(f"Old color: {self.old_color}")
                print(f"New color: {curr_color}")
                print(f"Event type: {event.type}")
                print(f"Event value: {event.value}")
                
                self.old_color = curr_color
                if curr_color is not None:
                    context.window_manager.coloraide_picker.mean = curr_color
                    print("Updated Coloraide picker")
            
        except Exception as e:
            print(f"Error in color monitor: {e}")
            print(f"Context mode: {context.mode}")
            
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        print("\n=== Starting Color Monitor... ===")
        print(f"Initial context mode: {context.mode}")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}