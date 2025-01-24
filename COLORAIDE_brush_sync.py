"""
Brush color synchronization system for Coloraide addon.
Handles direct brush color updates and propagation to picker.
"""

import bpy
from .COLORAIDE_utils import rgb_to_lab, lab_to_rgb, rgb_float_to_bytes
from contextlib import contextmanager

# Update state flags
_UPDATING_BRUSH = False

@contextmanager
def brush_update_lock():
    """Prevent recursive brush updates"""
    global _UPDATING_BRUSH
    if _UPDATING_BRUSH:
        yield False
        return
    _UPDATING_BRUSH = True
    try:
        yield True
    finally:
        _UPDATING_BRUSH = False

def is_brush_updating():
    """Check if brush update is in progress"""
    return _UPDATING_BRUSH

def sync_picker_from_brush(context, brush_color):
    """Update picker properties from brush color without triggering sync_all"""
    if is_brush_updating():
        return
        
    with brush_update_lock() as acquired:
        if not acquired:
            return
            
        wm = context.window_manager
        
        # Update picker means
        wm.coloraide_picker.suppress_updates = True
        wm.coloraide_picker.mean = brush_color
        wm.coloraide_picker.current = brush_color
        wm.coloraide_picker.suppress_updates = False
        
        # Update RGB values
        wm.coloraide_rgb.suppress_updates = True
        rgb_bytes = rgb_float_to_bytes(brush_color) 
        wm.coloraide_rgb.red = rgb_bytes[0]
        wm.coloraide_rgb.green = rgb_bytes[1]
        wm.coloraide_rgb.blue = rgb_bytes[2]
        wm.coloraide_rgb.suppress_updates = False
        
        # Update LAB
        wm.coloraide_lab.suppress_updates = True
        lab = rgb_to_lab(brush_color)
        wm.coloraide_lab.lightness = lab[0]
        wm.coloraide_lab.a = lab[1] 
        wm.coloraide_lab.b = lab[2]
        wm.coloraide_lab.suppress_updates = False
        
        # Update wheel
        wm.coloraide_wheel.suppress_updates = True
        wm.coloraide_wheel.color = (*brush_color, 1.0)
        wm.coloraide_wheel.suppress_updates = False

def sync_brush_from_picker(context, color):
    """Update brush colors directly from picker without full sync"""
    if is_brush_updating():
        return
        
    with brush_update_lock() as acquired:
        if not acquired:
            return
            
        ts = context.tool_settings
        
        # Update all relevant brushes directly
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = color
            
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = color

def update_brush_color(context, color):
    """Update brush color and propagate to picker"""
    sync_brush_from_picker(context, color)
    sync_picker_from_brush(context, color)

__all__ = [
    'sync_picker_from_brush',
    'sync_brush_from_picker', 
    'update_brush_color',
    'is_brush_updating'
]