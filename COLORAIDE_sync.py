"""
Central color synchronization system for Coloraide addon.
Manages bidirectional updates between all color representations.
"""

import bpy
from .COLORAIDE_utils import (
    rgb_to_lab,
    lab_to_rgb,
    rgb_to_hsv,
    hsv_to_rgb,
    rgb_to_hex,
    hex_to_rgb,
    rgb_float_to_bytes,
    UpdateFlags,
    is_updating
)

class ColorUpdateManager:
    """Manages color updates and synchronization across all components"""
    
    def __init__(self):
        self._current_update = None
        
    def sync_from_picker(self, context, color):
        """Synchronize all components from picker color (RGB float values)"""
        wm = context.window_manager
        
        # Bypass all updates if being updated from elsewhere
        if is_updating('picker'):
            return
            
        with UpdateFlags('picker'):
            # Update RGB
            rgb_bytes = rgb_float_to_bytes(color)
            wm.coloraide_rgb.red = rgb_bytes[0]
            wm.coloraide_rgb.green = rgb_bytes[1]
            wm.coloraide_rgb.blue = rgb_bytes[2]
            
            # Update LAB
            lab = rgb_to_lab(color)
            wm.coloraide_lab.lightness = lab[0]
            wm.coloraide_lab.a = lab[1]
            wm.coloraide_lab.b = lab[2]
            
            # Update HSV
            hsv = rgb_to_hsv(color)
            wm.coloraide_hsv.hue = hsv[0] * 360.0
            wm.coloraide_hsv.saturation = hsv[1] * 100.0
            wm.coloraide_hsv.value = hsv[2] * 100.0
            
            # Update Hex
            wm.coloraide_hex.value = rgb_to_hex(color)
            
            # Update Wheel
            wm.coloraide_wheel.color = (*color, 1.0)
            
            # Update brush colors
            ts = context.tool_settings
            if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
                ts.gpencil_paint.brush.color = color
            
            if hasattr(ts, 'image_paint') and ts.image_paint.brush:
                ts.image_paint.brush.color = color
                if ts.unified_paint_settings.use_unified_color:
                    ts.unified_paint_settings.color = color
    
    def sync_from_rgb(self, context, rgb_bytes):
        """Synchronize from RGB byte values (0-255)"""
        if is_updating('rgb'):
            return
            
        with UpdateFlags('rgb'):
            rgb_float = tuple(c / 255.0 for c in rgb_bytes)
            self.sync_from_picker(context, rgb_float)
    
    def sync_from_lab(self, context, lab_values):
        """Synchronize from LAB values"""
        if is_updating('lab'):
            return
            
        with UpdateFlags('lab'):
            rgb_float = lab_to_rgb(lab_values)
            self.sync_from_picker(context, rgb_float)
    
    def sync_from_hsv(self, context, hsv_values):
        """Synchronize from HSV values (H: 0-360, S/V: 0-100)"""
        if is_updating('hsv'):
            return
            
        with UpdateFlags('hsv'):
            hsv_normalized = (
                hsv_values[0] / 360.0,
                hsv_values[1] / 100.0,
                hsv_values[2] / 100.0
            )
            rgb_float = hsv_to_rgb(hsv_normalized)
            self.sync_from_picker(context, rgb_float)
    
    def sync_from_hex(self, context, hex_value):
        """Synchronize from hex color string"""
        if is_updating('hex'):
            return
            
        with UpdateFlags('hex'):
            rgb_float = hex_to_rgb(hex_value)
            self.sync_from_picker(context, rgb_float)
    
    def sync_from_wheel(self, context, wheel_color):
        """Synchronize from color wheel (RGBA)"""
        if is_updating('wheel'):
            return
            
        with UpdateFlags('wheel'):
            rgb_float = tuple(wheel_color[:3])
            self.sync_from_picker(context, rgb_float)
    
    def sync_from_history(self, context, history_color):
        """Synchronize from history color selection"""
        if is_updating('history'):
            return
            
        with UpdateFlags('history'):
            self.sync_from_picker(context, history_color)
    
    def sync_from_brush(self, context, brush_color):
        """Synchronize from brush color changes"""
        if is_updating('brush'):
            return
            
        with UpdateFlags('brush'):
            self.sync_from_picker(context, brush_color)

# Global instance
update_manager = ColorUpdateManager()

def sync_all(context, source, color):
    """
    Main synchronization function called by components.
    
    Args:
        context: Blender context
        source: String identifying update source ('picker', 'rgb', etc.)
        color: New color value in source's format
    """
    if is_updating(source):
        return
        
    try:
        if source == 'picker':
            update_manager.sync_from_picker(context, color)
        elif source == 'rgb':
            update_manager.sync_from_rgb(context, color)
        elif source == 'lab':
            update_manager.sync_from_lab(context, color)
        elif source == 'hsv':
            update_manager.sync_from_hsv(context, color)
        elif source == 'hex':
            update_manager.sync_from_hex(context, color)
        elif source == 'wheel':
            update_manager.sync_from_wheel(context, color)
        elif source == 'history':
            update_manager.sync_from_history(context, color)
        elif source == 'brush':
            update_manager.sync_from_brush(context, color)
    except Exception as e:
        print(f"Error in sync_all: {e}")

__all__ = ['sync_all', 'update_manager']