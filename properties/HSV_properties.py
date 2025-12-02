"""HSV Properties with optimized response and relative adjustment mode"""

import bpy
from bpy.props import FloatProperty, BoolProperty
from bpy.types import PropertyGroup
from ..import COLORAIDE_sync
from ..import COLORAIDE_utils

class ColoraideHSVProperties(PropertyGroup):
    suppress_updates: BoolProperty(default=False)
    
    def update_hsv_values(self, context):
        if COLORAIDE_sync.is_updating() or self.suppress_updates:
            return
        hsv_values = (self.hue, self.saturation, self.value)
        # Use RELATIVE mode for slider adjustments
        COLORAIDE_sync.sync_all(context, 'hsv', hsv_values, mode='relative')

    hue: FloatProperty(
        name="H",
        min=0.0,
        max=360.0,
        default=0.0,
        precision=0,
        step=100,
        update=update_hsv_values
    )
    
    saturation: FloatProperty(
        name="S",
        min=0.0,
        max=100.0,
        default=0.0,
        precision=0,
        step=100,
        subtype='PERCENTAGE',
        update=update_hsv_values
    )
    
    value: FloatProperty(
        name="V",
        min=0.0,
        max=100.0,
        default=100.0,
        precision=0,
        step=100,
        subtype='PERCENTAGE',
        update=update_hsv_values
    )