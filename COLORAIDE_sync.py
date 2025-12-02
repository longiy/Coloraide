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