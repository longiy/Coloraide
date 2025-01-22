"""
Property definitions for color wheel with bidirectional synchronization.
"""

import bpy
from bpy.props import FloatProperty, FloatVectorProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_utils import UpdateFlags

def sync_wheel_from_color(context, color):
    """
    Synchronize color wheel from RGB color.
    
    Args:
        context: Blender context
        color: Tuple of RGB values (0-1)
    """
    with UpdateFlags('wheel'):
        wm = context.window_manager
        if hasattr(wm, 'coloraide_wheel'):
            # Convert RGB to wheel color (RGBA)
            wm.coloraide_wheel.color = (*color, 1.0)

def update_from_wheel(self, context):
    """Update handler for color wheel changes"""
    with UpdateFlags('wheel'):
        # Extract RGB from wheel color (ignoring alpha)
        color = tuple(self.color[:3])
        
        # Update picker mean (this will trigger sync of all other inputs)
        picker = context.window_manager.coloraide_picker
        picker.mean = color

class ColoraideWheelProperties(PropertyGroup):
    """Properties for color wheel"""
    
    scale: FloatProperty(
        name="Wheel Size",
        description="Adjust the size of the color wheel",
        min=1.0,
        max=3.0,
        default=1.5,
        step=10,
        precision=1
    )
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=update_from_wheel
    )