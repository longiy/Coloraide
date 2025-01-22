"""
HSV color space properties with bidirectional synchronization.
"""

import bpy
from bpy.props import FloatProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_utils import (
    hsv_to_rgb,
    rgb_to_hsv,
    UpdateFlags
)

def sync_hsv_from_rgb(context, rgb_color):
    """
    Synchronize HSV values from RGB color.
    
    Args:
        context: Blender context
        rgb_color: Tuple of RGB values (0-1)
    """
    with UpdateFlags('hsv'):
        wm = context.window_manager
        if hasattr(wm, 'coloraide_hsv'):
            # Use rgb_to_hsv from COLORAIDE_utils
            hsv_values = rgb_to_hsv(rgb_color)
            wm.coloraide_hsv.hue = hsv_values[0] * 360.0
            wm.coloraide_hsv.saturation = hsv_values[1] * 100.0
            wm.coloraide_hsv.value = hsv_values[2] * 100.0

def update_hsv(self, context):
    """Update handler for HSV slider changes"""
    with UpdateFlags('hsv'):
        # Convert HSV to RGB using COLORAIDE_utils
        hsv = (
            self.hue / 360.0,
            self.saturation / 100.0,
            self.value / 100.0
        )
        rgb = hsv_to_rgb(hsv)
        
        # Update picker.mean (will trigger sync of other inputs)
        picker = context.window_manager.coloraide_picker
        picker.mean = rgb

class ColoraideHSVProperties(PropertyGroup):
    """Properties for HSV color sliders"""
    
    hue: FloatProperty(
        name="H",
        description="Hue (0-360°)",
        default=0.0,
        min=0.0,
        max=360.0,
        precision=1,
        update=update_hsv
    )
    
    saturation: FloatProperty(
        name="S",
        description="Saturation (0-100%)",
        default=0.0,
        min=0.0,
        max=100.0,
        precision=1,
        update=update_hsv
    )
    
    value: FloatProperty(
        name="V",
        description="Value (0-100%)",
        default=100.0,
        min=0.0,
        max=100.0,
        precision=1,
        update=update_hsv
    )