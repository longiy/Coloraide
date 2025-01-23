"""
Color monitor system for Coloraide addon.
"""

import bpy
from bpy.types import Operator
from .COLORAIDE_sync import sync_all
from .COLORAIDE_utils import is_updating

class COLOR_OT_monitor(Operator):
    """Monitor color changes and keep all components synchronized"""
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    # Store previous color to detect changes
    old_color = None
    
    def check_color_update(self, context):
        """Check for brush color changes and sync if needed"""
        try:
            # Get current brush color
            ts = context.tool_settings
            curr_color = None
            
            if context.mode == 'PAINT_GPENCIL' and ts.gpencil_paint.brush:
                curr_color = tuple(ts.gpencil_paint.brush.color)
            elif ts.image_paint and ts.image_paint.brush:
                curr_color = tuple(ts.image_paint.brush.color)
            
            # If color changed and not from our own updates
            if curr_color != self.old_color and curr_color is not None:
                if not is_updating('brush'):
                    # Use central sync system
                    sync_all(context, 'brush', curr_color)
                    self.old_color = curr_color
                    
        except Exception as e:
            print(f"Color monitor error: {e}")
    
    def modal(self, context, event):
        self.check_color_update(context)
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def start_color_monitor():
    """Start the color monitor with delay to ensure context is ready"""
    try:
        if bpy.context and bpy.context.window_manager:
            bpy.ops.color.monitor('INVOKE_DEFAULT')
            return None  # Unregister timer
        return 0.1  # Try again in 0.1 seconds
    except Exception as e:
        print(f"Error starting color monitor: {e}")
        return None  # Unregister timer on error

def register():
    bpy.utils.register_class(COLOR_OT_monitor)
    # Start monitor with delay
    bpy.app.timers.register(start_color_monitor, first_interval=0.1)

def unregister():
    bpy.utils.unregister_class(COLOR_OT_monitor)