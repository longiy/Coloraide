"""
Central color synchronization system for Coloraide addon.
"""

import bpy
from contextlib import contextmanager
from .COLORAIDE_utils import (
    rgb_to_lab,
    lab_to_rgb,
    rgb_to_hsv,
    hsv_to_rgb,
    # rgb_to_hex,
    # hex_to_rgb,
    rgb_float_to_bytes
)

# Global update state
_UPDATING = False

def is_updating():
    """Check if any update is in progress"""
    return _UPDATING

@contextmanager
def update_lock():
    """Context manager to prevent recursive updates"""
    global _UPDATING
    if _UPDATING:
        yield False
        return
    _UPDATING = True
    try:
        yield True
    finally:
        _UPDATING = False

def sync_all(context, source, color):
    """Synchronize all color spaces from source"""
    if is_updating():
        return
        
    with update_lock() as acquired:
        if not acquired:
            return
            
        wm = context.window_manager
        
        # Convert input to RGB float (0-1)
        if source == 'rgb':
            rgb_float = tuple(c / 255.0 for c in color)
        elif source == 'lab': 
            rgb_float = lab_to_rgb(color)
        elif source == 'hsv':
            hsv_norm = (color[0]/360.0, color[1]/100.0, color[2]/100.0)
            rgb_float = hsv_to_rgb(hsv_norm)
        elif source == 'hex':
            rgb_float = hex_to_rgb(color)
        else:
            rgb_float = tuple(color[:3])

        # Update all color spaces
        wm.coloraide_picker.suppress_updates = True
        wm.coloraide_picker.mean = rgb_float
        wm.coloraide_picker.current = rgb_float
        wm.coloraide_picker.suppress_updates = False

        wm.coloraide_rgb.suppress_updates = True
        rgb_bytes = rgb_float_to_bytes(rgb_float)
        wm.coloraide_rgb.red = rgb_bytes[0]
        wm.coloraide_rgb.green = rgb_bytes[1]
        wm.coloraide_rgb.blue = rgb_bytes[2]
        wm.coloraide_rgb.suppress_updates = False

        wm.coloraide_lab.suppress_updates = True
        lab = rgb_to_lab(rgb_float)
        wm.coloraide_lab.lightness = lab[0]
        wm.coloraide_lab.a = lab[1]
        wm.coloraide_lab.b = lab[2]
        wm.coloraide_lab.suppress_updates = False

        wm.coloraide_hsv.suppress_updates = True
        hsv = rgb_to_hsv(rgb_float)
        wm.coloraide_hsv.hue = hsv[0] * 360.0
        wm.coloraide_hsv.saturation = hsv[1] * 100.0
        wm.coloraide_hsv.value = hsv[2] * 100.0
        wm.coloraide_hsv.suppress_updates = False

        wm.coloraide_wheel.suppress_updates = True
        wm.coloraide_wheel.color = (*rgb_float, 1.0)
        wm.coloraide_wheel.suppress_updates = False

        # Update brush colors without mode check
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = rgb_float
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = rgb_float
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = rgb_float

__all__ = ['sync_all', 'is_updating']