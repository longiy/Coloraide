"""
Simplified color synchronization system for Blender 5.0+
All colors are handled in scene linear color space internally.
NOW WITH RELATIVE ADJUSTMENT MODE for live-synced properties.
FIX: Added recursion guards for live sync updates.
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
_PREVIOUS_COLOR = (0.5, 0.5, 0.5)  # Track previous color for delta calculations
_UPDATING_LIVE_SYNC = False  # FIX 1: Guard for live sync recursion

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


@contextmanager
def live_sync_lock():
    """Context manager to prevent recursive live sync updates."""
    global _UPDATING_LIVE_SYNC
    if _UPDATING_LIVE_SYNC:
        yield False
        return
    _UPDATING_LIVE_SYNC = True
    try:
        yield True
    finally:
        _UPDATING_LIVE_SYNC = False


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


def is_updating_live_sync():
    """Check if live sync update is in progress."""
    return _UPDATING_LIVE_SYNC


def sync_all(context, source, color_value, mode='absolute'):
    """
    Unified synchronization function - updates all Coloraide properties from any source.
    NOW WITH RELATIVE MODE for live-synced properties.
    
    Args:
        context: Blender context
        source: Source of the color change ('picker', 'wheel', 'rgb', 'hsv', 'lab', 'hex', 
                'history', 'palette', 'brush', 'object_colors')
        color_value: Color data (format depends on source)
        mode: 'absolute' (default, replace color) or 'relative' (adjust by delta)
    
    Color value formats by source:
        - picker/wheel/history/palette/brush/object_colors: (r, g, b) scene linear
        - rgb: (r, g, b) bytes 0-255
        - hsv: (h, s, v) where h=0-360, s=0-100, v=0-100
        - lab: (L, a, b) where L=0-100, a=-128-127, b=-128-127
        - hex: "#RRGGBB" string
    """
    global _PREVIOUS_COLOR
    
    with update_lock(source) as acquired:
        if not acquired:
            return
        
        wm = context.window_manager
        
        # Convert input to scene linear RGB
        if source in ('picker', 'wheel', 'history', 'palette', 'brush', 'object_colors'):
            rgb_linear = tuple(color_value[:3])
        elif source == 'rgb':
            rgb_linear = rgb_bytes_to_linear(color_value)
        elif source == 'hsv':
            h_norm = color_value[0] / 360.0
            s_norm = color_value[1] / 100.0
            v_norm = color_value[2] / 100.0
            rgb_linear = hsv_to_rgb((h_norm, s_norm, v_norm))
        elif source == 'lab':
            rgb_linear = lab_to_rgb(color_value)
        elif source == 'hex':
            rgb_linear = hex_to_linear(color_value)
        else:
            print(f"Unknown source: {source}")
            return
        
        # Calculate delta for relative mode
        delta = None
        if mode == 'relative':
            delta = tuple(new - old for new, old in zip(rgb_linear, _PREVIOUS_COLOR))
        
        # Update previous color
        _PREVIOUS_COLOR = rgb_linear
        
        # Update picker (mean color)
        if source != 'picker':
            wm.coloraide_picker.suppress_updates = True
            wm.coloraide_picker.mean = rgb_linear
            wm.coloraide_picker.suppress_updates = False
        
        # Update color wheel
        if source != 'wheel':
            wm.coloraide_wheel.suppress_updates = True
            wm.coloraide_wheel.color = tuple(rgb_linear) + (1.0,)
            wm.coloraide_wheel.suppress_updates = False
        
        # Update RGB sliders (convert to bytes)
        if source != 'rgb':
            rgb_bytes = rgb_linear_to_bytes(rgb_linear)
            wm.coloraide_rgb.suppress_updates = True
            wm.coloraide_rgb.red = rgb_bytes[0]
            wm.coloraide_rgb.green = rgb_bytes[1]
            wm.coloraide_rgb.blue = rgb_bytes[2]
            # Update preview colors
            wm.coloraide_rgb.red_preview = (rgb_linear[0], 0.0, 0.0)
            wm.coloraide_rgb.green_preview = (0.0, rgb_linear[1], 0.0)
            wm.coloraide_rgb.blue_preview = (0.0, 0.0, rgb_linear[2])
            wm.coloraide_rgb.suppress_updates = False
        
        # Update HSV sliders
        if source != 'hsv':
            hsv = rgb_to_hsv(rgb_linear)
            wm.coloraide_hsv.suppress_updates = True
            wm.coloraide_hsv.hue = hsv[0] * 360.0
            wm.coloraide_hsv.saturation = hsv[1] * 100.0
            wm.coloraide_hsv.value = hsv[2] * 100.0
            wm.coloraide_hsv.suppress_updates = False
        
        # Update LAB sliders
        if source != 'lab':
            lab = rgb_to_lab(rgb_linear)
            wm.coloraide_lab.suppress_updates = True
            wm.coloraide_lab.lightness = lab[0]
            wm.coloraide_lab.a = lab[1]
            wm.coloraide_lab.b = lab[2]
            wm.coloraide_lab.suppress_updates = False
        
        # Update hex input
        if source != 'hex':
            hex_value = linear_to_hex(rgb_linear)
            wm.coloraide_hex.suppress_updates = True
            wm.coloraide_hex.value = hex_value
            wm.coloraide_hex.prev_value = hex_value
            wm.coloraide_hex.suppress_updates = False
        
        # Update brush color (unless source is brush to prevent loop)
        if source != 'brush':
            try:
                ModeManager.set_brush_color(context, rgb_linear)
            except Exception as e:
                pass  # Silent fail if not in paint mode
        
        # Update palette preview
        if source != 'palette':
            wm.coloraide_palette.suppress_updates = True
            wm.coloraide_palette.preview_color = rgb_linear
            wm.coloraide_palette.suppress_updates = False
        
        # Update live-synced object colors (with mode)
        # FIX 1: Use live sync lock to prevent recursion
        if source != 'object_colors':
            with live_sync_lock() as acquired:
                if acquired:
                    try:
                        from .operators.OBJECT_COLORS_OT import update_live_synced_properties
                        update_live_synced_properties(context, rgb_linear, mode=mode, delta=delta)
                    except ImportError:
                        pass  # Object colors module not yet loaded


__all__ = ['sync_all', 'is_updating', 'update_lock', 'is_updating_live_sync', 'live_sync_lock']