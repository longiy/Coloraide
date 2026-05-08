"""
Brush color synchronization for Blender 5.0+
Simplified using ModeManager - only handles current mode's brush.
"""

import bpy
from contextlib import contextmanager
from .COLORAIDE_mode_manager import ModeManager
from .COLORAIDE_sync import sync_all
from . import COLORAIDE_state as _state

@contextmanager
def brush_update_lock():
    """Prevent recursive brush updates."""
    if _state.is_brush_updating:
        yield False
        return
    _state.is_brush_updating = True
    try:
        yield True
    finally:
        _state.is_brush_updating = False


def is_brush_updating():
    """Check if brush update is in progress."""
    return _state.is_brush_updating


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
