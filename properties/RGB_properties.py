"""
Property definitions for RGB color sliders with improved synchronization.
"""

import bpy
from bpy.props import IntProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_utils import (
    rgb_bytes_to_float,
    rgb_float_to_bytes,
    UpdateFlags
)

def sync_rgb_from_brush(context, rgb_color):
    """
    Synchronize RGB values from brush color.
    
    Args:
        context: Blender context
        rgb_color: Tuple of RGB float values (0-1)
    """
    with UpdateFlags('rgb'):
        wm = context.window_manager
        if hasattr(wm, 'coloraide_rgb'):
            # Convert float RGB to bytes using utility function
            rgb_bytes = rgb_float_to_bytes(rgb_color)
            wm.coloraide_rgb.red = rgb_bytes[0]
            wm.coloraide_rgb.green = rgb_bytes[1]
            wm.coloraide_rgb.blue = rgb_bytes[2]

def update_rgb_byte(self, context):
    """Update handler for RGB byte value changes"""
    with UpdateFlags('rgb'):
        # Convert byte RGB to float using utility function
        rgb_float = rgb_bytes_to_float((self.red, self.green, self.blue))
        
        # Update picker values (this will trigger synchronization of other inputs)
        picker = context.window_manager.coloraide_picker
        picker.mean = rgb_float
        picker.current = rgb_float

class ColoraideRGBProperties(PropertyGroup):
    """Properties for RGB color sliders"""
    
    red: IntProperty(
        name="R",
        description="Red (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte
    )
    
    green: IntProperty(
        name="G",
        description="Green (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte
    )
    
    blue: IntProperty(
        name="B",
        description="Blue (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte
    )