# COLORAIDE_palette_bridge.py
import bpy
from bpy.app.handlers import persistent
from contextlib import contextmanager

# State management
_PALETTE_SYNC_ACTIVE = False
_PALETTE_LOCK = False

@contextmanager
def palette_sync_lock():
    """Prevent recursive palette updates"""
    global _PALETTE_LOCK
    if _PALETTE_LOCK:
        yield False
        return
    _PALETTE_LOCK = True
    try:
        yield True
    finally:
        _PALETTE_LOCK = False

def is_palette_locked():
    """Check if palette sync is locked"""
    return _PALETTE_LOCK

class PaletteUpdateHandler:
    """Handles synchronization between Blender palette and Coloraide"""
    
    @classmethod
    def ensure_active_palette(cls, context):
        """Ensure there's an active palette"""
        ts = context.tool_settings
        settings = ts.gpencil_paint if context.mode == 'PAINT_GPENCIL' else ts.image_paint
        
        if not settings.palette:
            # Create default palette if none exists
            palette = bpy.data.palettes.new("Coloraide Palette")
            settings.palette = palette
            return palette
        return settings.palette
    
    @classmethod
    def sync_from_palette(cls, context, color):
        """Sync color from palette to Coloraide"""
        if is_palette_locked():
            return
            
        with palette_sync_lock():
            wm = context.window_manager
            if not hasattr(wm, 'coloraide_picker'):
                return
                
            # Update picker without triggering full sync
            wm.coloraide_picker.suppress_updates = True
            wm.coloraide_picker.mean = color
            wm.coloraide_picker.current = color
            wm.coloraide_picker.suppress_updates = False
            
            # Now trigger full sync
            from .COLORAIDE_sync import sync_all
            sync_all(context, 'palette', color)
    
    @classmethod
    def sync_to_palette(cls, context, color):
        """Add color to palette from Coloraide"""
        if is_palette_locked():
            return
            
        with palette_sync_lock():
            palette = cls.ensure_active_palette(context)
            if not palette:
                return
                
            # Add new color to palette
            new_color = palette.colors.new()
            new_color.color = color
            
            # Set as active color
            palette.colors.active = new_color

@persistent
def initialize_palette_bridge(scene):
    """Initialize palette bridge on file load"""
    global _PALETTE_SYNC_ACTIVE
    _PALETTE_SYNC_ACTIVE = True

def register():
    bpy.app.handlers.load_post.append(initialize_palette_bridge)
    
def unregister():
    global _PALETTE_SYNC_ACTIVE
    _PALETTE_SYNC_ACTIVE = False
    if initialize_palette_bridge in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(initialize_palette_bridge)