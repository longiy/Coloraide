"""
RGB color slider properties with synchronization using central sync system.
"""

import bpy
from bpy.props import IntProperty, FloatProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating

def update_rgb_bytes(self, context):
    """Update handler for RGB byte value changes"""
    if is_updating('rgb'):
        return
        
    # Package RGB values as a tuple of bytes (0-255)
    rgb_bytes = (self.red, self.green, self.blue)
    sync_all(context, 'rgb', rgb_bytes)

def update_alpha(self, context):
    """Update handler for alpha value changes"""
    if is_updating('rgb'):
        return
        
    # Store alpha value for use in mixing/blending
    context.window_manager.coloraide_picker.alpha = self.alpha

class ColoraideRGBProperties(PropertyGroup):
    """Properties for RGB color sliders"""
    
    red: IntProperty(
        name="R",
        description="Red (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_bytes
    )
    
    green: IntProperty(
        name="G",
        description="Green (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_bytes
    )
    
    blue: IntProperty(
        name="B",
        description="Blue (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_bytes
    )
    
    alpha: FloatProperty(
        name="A",
        description="Alpha (0-1)",
        min=0.0,
        max=1.0,
        default=1.0,
        precision=3,
        update=update_alpha
    )