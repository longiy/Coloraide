# CPICKER_properties.py
import bpy
from bpy.props import IntProperty, FloatVectorProperty, BoolProperty, StringProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraidePickerProperties(PropertyGroup):
    suppress_updates: BoolProperty(default=False)

    def update_mean_color(self, context):
        if is_updating() or self.suppress_updates:
            return
        sync_all(context, 'picker', self.mean)

    def update_current_color(self, context):
        if is_updating() or self.suppress_updates:
            return
        # Only update display without triggering syncs
        pass

    custom_size: IntProperty(
        description="Size of the sample square area in pixels",
        default=10,
        min=1,
        soft_max=100,
        soft_min=5
    )
   
    mean: FloatVectorProperty(
        name="Mean Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(0.5, 0.5, 0.5),
        update=update_mean_color
    )

    current: FloatVectorProperty(
        name="Current Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0),
    )

    max: FloatVectorProperty(
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0)
    )

    min: FloatVectorProperty(
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(0.0, 0.0, 0.0)
    )

    median: FloatVectorProperty(
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(0.5, 0.5, 0.5)
    )