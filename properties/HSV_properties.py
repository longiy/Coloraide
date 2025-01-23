"""
HSV color slider properties with synchronization using central sync system.
"""

import bpy
from bpy.props import FloatProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating

def update_hsv_values(self, context):
    """Update handler for HSV value changes"""
    if is_updating('hsv'):
        return
        
    # Package HSV values as a tuple (keeping original ranges)
    hsv_values = (self.hue, self.saturation, self.value)
    sync_all(context, 'hsv', hsv_values)

class ColoraideHSVProperties(PropertyGroup):
    """Properties for HSV color sliders"""
    
    hue: FloatProperty(
        name="H",
        description="Hue (0-360°)",
        default=0.0,
        min=0.0,
        max=360.0,
        precision=1,
        update=update_hsv_values
    )
    
    saturation: FloatProperty(
        name="S",
        description="Saturation (0-100%)",
        default=0.0,
        min=0.0,
        max=100.0,
        precision=1,
        subtype='PERCENTAGE',
        update=update_hsv_values
    )
    
    value: FloatProperty(
        name="V",
        description="Value/Brightness (0-100%)",
        default=100.0,
        min=0.0,
        max=100.0,
        precision=1,
        subtype='PERCENTAGE',
        update=update_hsv_values
    )