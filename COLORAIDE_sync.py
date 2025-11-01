"""
Simplified color synchronization system for Blender 5.0+
All colors are handled in scene linear color space internally.
"""

import bpy
from contextlib import contextmanager
from .COLORAIDE_utils import (
    rgb_to_lab, 
    lab_to_rgb,
    rgb_to_hsv,
    hsv_to_rgb
)
from .COLORAIDE_colorspace import (
    rgb_linear_to_bytes,
    rgb_bytes_to_linear,
    linear_to_hex,
    hex_to_linear
)
from .COLORAIDE_mode_manager import ModeManager

_UPDATING = False
_UPDATE_SOURCE = None

@contextmanager 
def update_lock(source=None):
    """Context manager to prevent recursive updates."""
    global _UPDATING, _UPDATE_SOURCE
    if _UPDATING:
        yield False
        return
    _UPDATING = True
    _UPDATE_SOURCE = source
    try:
        yield True
    finally:
        _UPDATING = False
        _UPDATE_SOURCE = None


def is_updating(source=None):
    """
    Check if an update is currently in progress.
    
    Args:
        source: Optional source identifier to check against
    
    Returns:
        bool: True if updating (and source doesn't match if provided)
    """
    if source:
        return _UPDATING and _UPDATE_SOURCE != source
    return _UPDATING


def sync_all(context, source, color):
    """
    Synchronize all Coloraide properties and current mode brush from a color change.
    
    This is the central synchronization function that:
    1. Converts input color to scene linear RGB (if not already)
    2. Updates all Coloraide UI properties
    3. Updates ONLY the current active mode's brush color
    
    Args:
        context: Blender context
        source: String identifier of what triggered the sync
                ('wheel', 'picker', 'hsv', 'rgb', 'lab', 'hex', 'history', 'palette', 'brush')
        color: Color data (format depends on source)
    
    Note: All internal Coloraide state is stored in scene linear color space.
          Conversions to/from sRGB happen only at UI boundaries.
    """
    if is_updating(source):
        return
    
    with update_lock(source) as acquired:
        if not acquired:
            return
        
        wm = context.window_manager
        
        # Convert input to scene linear RGB [0.0, 1.0]
        rgb_linear = _convert_to_linear(source, color, wm)
        
        # Update all Coloraide properties (in scene linear space)
        _update_coloraide_properties(wm, rgb_linear)
        
        # Update current mode's brush color
        ModeManager.set_brush_color(context, rgb_linear)


def _convert_to_linear(source, color, wm):
    """
    Convert various color input formats to scene linear RGB.
    
    Args:
        source: Source identifier
        color: Color data in source-specific format
        wm: Window manager (for accessing current LAB values)
    
    Returns:
        tuple: (r, g, b) in scene linear space [0.0, 1.0]
    """
    if source == 'rgb':
        # RGB bytes (0-255) in sRGB space
        return rgb_bytes_to_linear(color)
    
    elif source == 'lab':
        # LAB values with near-zero rounding
        current_lab = [
            0.0 if abs(wm.coloraide_lab.lightness) < 0.1 else float(wm.coloraide_lab.lightness),
            0.0 if abs(wm.coloraide_lab.a) < 0.1 else float(wm.coloraide_lab.a),
            0.0 if abs(wm.coloraide_lab.b) < 0.1 else float(wm.coloraide_lab.b)
        ]
        
        for i, val in enumerate(color):
            val = 0.0 if abs(float(val)) < 0.1 else float(val)
            if abs(val - current_lab[i]) > 0.0001:
                current_lab[i] = val
        
        return lab_to_rgb(tuple(current_lab))
    
    elif source == 'hsv':
        # HSV display values (H: 0-360, S: 0-100, V: 0-100) -> normalized
        hsv_norm = (color[0] / 360.0, color[1] / 100.0, color[2] / 100.0)
        return hsv_to_rgb(hsv_norm)
    
    elif source == 'hex':
        # Hex string (sRGB)
        if isinstance(color, str):
            return hex_to_linear(color)
        return tuple(color[:3])
    
    else:
        # Default: assume already in scene linear RGB (picker, wheel, history, palette, brush)
        return tuple(color[:3])


def _update_coloraide_properties(wm, rgb_linear):
    """
    Update all Coloraide UI properties from scene linear RGB color.
    
    Args:
        wm: Window manager
        rgb_linear: Tuple of (r, g, b) in scene linear space [0.0, 1.0]
    """
    # Update RGB properties (display as sRGB bytes)
    wm.coloraide_rgb.suppress_updates = True
    rgb_bytes = rgb_linear_to_bytes(rgb_linear)
    wm.coloraide_rgb.red = rgb_bytes[0]
    wm.coloraide_rgb.green = rgb_bytes[1]
    wm.coloraide_rgb.blue = rgb_bytes[2]
    wm.coloraide_rgb.suppress_updates = False
    
    # Update LAB
    wm.coloraide_lab.suppress_updates = True
    lab = rgb_to_lab(rgb_linear)
    wm.coloraide_lab.lightness = round(lab[0])
    wm.coloraide_lab.a = round(lab[1])
    wm.coloraide_lab.b = round(lab[2])
    wm.coloraide_lab.suppress_updates = False
    
    # Update HSV
    wm.coloraide_hsv.suppress_updates = True
    hsv = rgb_to_hsv(rgb_linear)
    wm.coloraide_hsv.hue = round(hsv[0] * 360.0)
    wm.coloraide_hsv.saturation = round(hsv[1] * 100.0)
    wm.coloraide_hsv.value = round(hsv[2] * 100.0)
    wm.coloraide_hsv.suppress_updates = False
    
    # Update picker mean (scene linear)
    wm.coloraide_picker.suppress_updates = True
    wm.coloraide_picker.mean = rgb_linear
    wm.coloraide_picker.suppress_updates = False
    
    # Update wheel (scene linear + alpha)
    wm.coloraide_wheel.suppress_updates = True
    wm.coloraide_wheel.color = (*rgb_linear, 1.0)
    wm.coloraide_wheel.suppress_updates = False
    
    # Update hex (convert to sRGB for hex representation)
    wm.coloraide_hex.suppress_updates = True
    hex_value = linear_to_hex(rgb_linear)
    wm.coloraide_hex.value = hex_value
    wm.coloraide_hex.suppress_updates = False


__all__ = ['sync_all', 'is_updating', 'update_lock']
