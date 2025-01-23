"""
Core property definitions for color picker functionality.
"""

import bpy
from bpy.props import IntProperty, FloatVectorProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import UpdateFlags, is_updating

def update_mean_color(self, context):
    """Update handler for mean color changes"""
    if is_updating('picker'):
        return
        
    sync_all(context, 'picker', self.mean)

def update_current_color(self, context):
    """Update handler for current (1x1 sample) color changes"""
    if is_updating('picker'):  
        return
        
    # Only update the current display without affecting other values
    pass  

class ColoraidePickerProperties(PropertyGroup):
    """Properties for core color picker functionality"""
    
    custom_size: IntProperty(
        name="Quick Pick Size",
        description="Custom tile size for quick picker",
        default=10,
        min=1,
        soft_max=100,
        soft_min=5
    )
    
    mean: FloatVectorProperty(
        name="Mean Color",
        description="The mean RGB values of the picked pixels",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(0.5, 0.5, 0.5),
        update=update_mean_color
    )
    
    current: FloatVectorProperty(
        name="Current Color",
        description="The current RGB values under the cursor",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_current_color
    )
    
    max: FloatVectorProperty(
        name="Maximum",
        description="The maximum RGB values in the sample area",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
    )
    
    min: FloatVectorProperty(
        name="Minimum",
        description="The minimum RGB values in the sample area",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0)
    )
    
    median: FloatVectorProperty(
        name="Median",
        description="The median RGB values in the sample area",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(0.5, 0.5, 0.5)
    )