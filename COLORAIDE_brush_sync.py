"""
Brush color synchronization for Blender 5.0+
Simplified using ModeManager - only handles current mode's brush.
"""

import bpy
from contextlib import contextmanager
from .COLORAIDE_mode_manager import ModeManager
from .COLORAIDE_sync import sync_all

_UPDATING_BRUSH = False

@contextmanager
def brush_update_lock():
    """Prevent recursive brush updates."""
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
    """Check if brush update is in progress."""
    return _UPDATING_BRUSH


def sync_coloraide_from_brush(context, brush_color):
    """
    Update all Coloraide properties from brush color (scene linear).
    Does NOT update the brush itself - only updates Coloraide UI.
    
    Args:
        context: Blender context
        brush_color: Tuple of (r, g, b) in scene linear space [0.0, 1.0]
    """
    if is_brush_updating():
        return
    
    with brush_update_lock() as acquired:
        if not acquired:
            return
        
        # Use sync_all with 'brush' source to update Coloraide
        # This will NOT trigger brush update (prevents loop)
        sync_all(context, 'brush', brush_color)


def update_brush_color(context, color):
    """
    Convenience function to update brush and sync to Coloraide.
    
    Args:
        context: Blender context
        color: Tuple of (r, g, b) in scene linear space [0.0, 1.0]
    """
    ModeManager.set_brush_color(context, color)
    sync_coloraide_from_brush(context, color)


__all__ = [
    'sync_coloraide_from_brush',
    'update_brush_color',
    'is_brush_updating'
]
