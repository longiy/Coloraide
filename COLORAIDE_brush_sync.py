"""
Brush color synchronization system for Coloraide addon.
Handles direct brush color updates and propagation to picker.
Updated for Blender 4.3+ API changes and history priority.
"""

import bpy
from .COLORAIDE_utils import rgb_to_lab, lab_to_rgb, hsv_to_rgb, rgb_to_hsv, rgb_float_to_bytes
from contextlib import contextmanager

# Update state flags
_UPDATING_BRUSH = False
_HISTORY_UPDATE_IN_PROGRESS = False

@contextmanager
def brush_update_lock():
    """Prevent recursive brush updates, with exception for history updates"""
    global _UPDATING_BRUSH
    
    # Check if a history update is in progress
    if _HISTORY_UPDATE_IN_PROGRESS:
        yield True  # Allow updates from history even if brush is already updating
        return
        
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

def set_history_update_flag(active=False):
    """Set the flag indicating a history update is in progress"""
    global _HISTORY_UPDATE_IN_PROGRESS
    _HISTORY_UPDATE_IN_PROGRESS = active

def check_brush_color(context, paint_settings):
    """Get current brush color from paint settings"""
    if not paint_settings or not paint_settings.brush:
        return None
        
    ts = context.tool_settings
    if ts.unified_paint_settings.use_unified_color:
        return tuple(ts.unified_paint_settings.color)
    
    if paint_settings.palette and paint_settings.palette.colors.active:
        # If active palette color exists, use it
        return tuple(paint_settings.palette.colors.active.color)
        
    return tuple(paint_settings.brush.color)

def sync_picker_from_brush(context, brush_color):
    """Update picker properties from brush color without triggering sync_all"""
    # Don't block updates from history
    if is_brush_updating() and not _HISTORY_UPDATE_IN_PROGRESS:
        return
        
    with brush_update_lock() as acquired:
        if not acquired and not _HISTORY_UPDATE_IN_PROGRESS:
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
        
        # Update HSV
        wm.coloraide_hsv.suppress_updates = True
        hsv = rgb_to_hsv(brush_color)
        wm.coloraide_hsv.hue = hsv[0] * 360.0
        wm.coloraide_hsv.saturation = hsv[1] * 100.0
        wm.coloraide_hsv.value = hsv[2] * 100.0
        wm.coloraide_hsv.suppress_updates = False
        
        # Update wheel
        wm.coloraide_wheel.suppress_updates = True
        wm.coloraide_wheel.color = (*brush_color, 1.0)
        wm.coloraide_wheel.suppress_updates = False

def sync_brush_from_picker(context, color, from_history=False):
    """Update brush colors directly from picker without full sync"""
    global _HISTORY_UPDATE_IN_PROGRESS
    
    # Set the history update flag if this update is from history
    if from_history:
        _HISTORY_UPDATE_IN_PROGRESS = True
    
    try:
        if is_brush_updating() and not _HISTORY_UPDATE_IN_PROGRESS:
            return
            
        with brush_update_lock() as acquired:
            if not acquired and not _HISTORY_UPDATE_IN_PROGRESS:
                return
                
            ts = context.tool_settings
            
            # Update Grease Pencil brush if available
            if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint and ts.gpencil_paint.brush:
                ts.gpencil_paint.brush.color = color
                if ts.unified_paint_settings.use_unified_color:
                    ts.unified_paint_settings.color = color
                    
            # Update Image Paint brush if available  
            if hasattr(ts, 'image_paint') and ts.image_paint and ts.image_paint.brush:
                ts.image_paint.brush.color = color
                if ts.unified_paint_settings.use_unified_color:
                    ts.unified_paint_settings.color = color
                    
            # Update Vertex Paint brush if available
            if hasattr(ts, 'vertex_paint') and ts.vertex_paint and ts.vertex_paint.brush:
                ts.vertex_paint.brush.color = color
                if ts.unified_paint_settings.use_unified_color:
                    ts.unified_paint_settings.color = color
    finally:
        if from_history:
            _HISTORY_UPDATE_IN_PROGRESS = False

def update_brush_color(context, color, from_history=False):
    """Update brush color and propagate to picker"""
    sync_brush_from_picker(context, color, from_history)
    sync_picker_from_brush(context, color)

__all__ = [
    'sync_picker_from_brush',
    'sync_brush_from_picker', 
    'update_brush_color',
    'is_brush_updating',
    'set_history_update_flag'
]