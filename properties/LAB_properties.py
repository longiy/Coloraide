"""
LAB color space properties with bidirectional synchronization.
"""

import bpy
from bpy.props import FloatProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_utils import (
    lab_to_rgb,
    rgb_to_lab,
    UpdateFlags
)

def sync_lab_from_rgb(context, rgb_color):
    """
    Synchronize LAB values from RGB color.
    
    Args:
        context: Blender context
        rgb_color: Tuple of RGB values (0-1)
    """
    with UpdateFlags('lab'):
        wm = context.window_manager
        if hasattr(wm, 'coloraide_lab'):
            # Use rgb_to_lab from COLORAIDE_utils
            lab_values = rgb_to_lab(rgb_color)
            wm.coloraide_lab.lightness = lab_values[0]
            wm.coloraide_lab.a = lab_values[1]
            wm.coloraide_lab.b = lab_values[2]

def update_lab(self, context):
    """Update handler for LAB slider changes"""
    with UpdateFlags('lab'):
        # Convert LAB to RGB using COLORAIDE_utils
        lab = (self.lightness, self.a, self.b)
        rgb = lab_to_rgb(lab)
        
        # Update picker.mean (will trigger sync of other inputs)
        picker = context.window_manager.coloraide_picker
        picker.mean = rgb

class ColoraideLABProperties(PropertyGroup):
    """Properties for LAB color sliders"""
    
    lightness: FloatProperty(
        name="L",
        description="Lightness (0-100)",
        default=50.0,
        min=0.0,
        max=100.0,
        precision=1,
        update=update_lab
    )
    
    a: FloatProperty(
        name="a",
        description="Green (-) to Red (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=1,
        update=update_lab
    )
    
    b: FloatProperty(
        name="b",
        description="Blue (-) to Yellow (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=1,
        update=update_lab
    )