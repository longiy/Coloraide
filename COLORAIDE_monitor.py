"""
Color monitor system for Coloraide addon.
Keeps all color components synchronized and monitors brush color changes.
"""

import bpy
from bpy.types import Operator
from .sync_utils import (
    sync_rgb_from_brush,
    sync_lab_from_rgb,
    sync_hsv_from_rgb, 
    sync_hex_from_rgb
)

class COLOR_OT_monitor(Operator):
    """Monitor color changes and keep all components synchronized"""
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    # Store previous color to detect changes
    old_color = None
    
    def sync_components(self, context, color):
        """Synchronize all color components with new color"""
        wm = context.window_manager
        
        # Update picker colors
        wm.coloraide_picker.mean = color
        wm.coloraide_picker.current = color
        
        # Update color wheel
        if hasattr(wm, 'coloraide_wheel'):
            wm.coloraide_wheel.color = (*color, 1.0)
            
        # Update RGB sliders
        if hasattr(wm, 'coloraide_rgb'):
            rgb_bytes = tuple(round(c * 255) for c in color)
            wm.coloraide_rgb.red = rgb_bytes[0]
            wm.coloraide_rgb.green = rgb_bytes[1]
            wm.coloraide_rgb.blue = rgb_bytes[2]
            
        # Update hex value
        if hasattr(wm, 'coloraide_hex'):
            wm.coloraide_hex.value = "#{:02X}{:02X}{:02X}".format(
                round(color[0] * 255),
                round(color[1] * 255),
                round(color[2] * 255)
            )
            
        # Update LAB values
        if hasattr(wm, 'coloraide_lab'):
            from .properties.LAB_properties import sync_lab_from_rgb
            sync_lab_from_rgb(context, color)
            
        # Update HSV values
        if hasattr(wm, 'coloraide_hsv'):
            from .properties.HSV_properties import sync_hsv_from_rgb
            sync_hsv_from_rgb(context, color)
    
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
                # Check if any component is currently updating
                if not any([
                    hasattr(context.window_manager, 'coloraide_rgb') and context.window_manager.coloraide_rgb.is_updating,
                    hasattr(context.window_manager, 'coloraide_lab') and context.window_manager.coloraide_lab.is_updating,
                    hasattr(context.window_manager, 'coloraide_hsv') and context.window_manager.coloraide_hsv.is_updating,
                    hasattr(context.window_manager, 'coloraide_hex') and context.window_manager.coloraide_hex.is_updating,
                ]):
                    self.sync_components(context, curr_color)
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