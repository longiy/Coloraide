"""
Property definitions for color wheel functionality.
"""

import bpy
from bpy.props import FloatProperty, FloatVectorProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating

def update_wheel_color(self, context):
    """Update handler for color wheel changes"""
    if is_updating('wheel'):
        return
        
    # Extract RGB from wheel color (ignoring alpha)
    color = tuple(self.color[:3])
    sync_all(context, 'wheel', color)

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
        update=update_wheel_color
    )