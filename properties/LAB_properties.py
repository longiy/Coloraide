"""
LAB color slider properties with synchronization using central sync system.
"""

import bpy
from bpy.props import FloatProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import UpdateFlags, is_updating

def update_lab_values(self, context):
    """Update handler for LAB value changes"""
    if is_updating('lab'):
        return
        
    # Package LAB values as a tuple
    lab_values = (self.lightness, self.a, self.b)
    sync_all(context, 'lab', lab_values)

class ColoraideLABProperties(PropertyGroup):
    """Properties for LAB color sliders"""
    
    lightness: FloatProperty(
        name="L",
        description="Lightness (0-100)",
        default=50.0,
        min=0.0,
        max=100.0,
        precision=1,
        update=update_lab_values
    )
    
    a: FloatProperty(
        name="a",
        description="Green (-) to Red (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=1,
        update=update_lab_values
    )
    
    b: FloatProperty(
        name="b",
        description="Blue (-) to Yellow (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=1,
        update=update_lab_values
    )