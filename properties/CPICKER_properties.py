"""Color picker properties - Blender 5.0+ (scene linear color space)"""

import bpy
from bpy.props import IntProperty, FloatVectorProperty, BoolProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraidePickerProperties(PropertyGroup):
    """
    Color picker properties.
    All colors stored in scene linear color space (Blender 5.0+ standard).
    """
    suppress_updates: BoolProperty(default=False)

    def update_mean_color(self, context):
        """Sync mean color (scene linear) to all other properties."""
        if is_updating() or self.suppress_updates:
            return
        # Color is already in scene linear space from picker
        sync_all(context, 'picker', self.mean)

    def update_current_color(self, context):
        """Current color is display-only, no sync needed."""
        if is_updating() or self.suppress_updates:
            return
        # Only update display without triggering syncs
        pass

    custom_size: IntProperty(
        name="Sample Size",
        description="Size of the sample square area in pixels",
        default=10,
        min=1,
        soft_max=100,
        soft_min=5
    )
   
    mean: FloatVectorProperty(
        name="Mean Color",
        description="Average color of sampled area (scene linear)",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(0.5, 0.5, 0.5),
        update=update_mean_color
    )

    current: FloatVectorProperty(
        name="Current Color",
        description="Single pixel color under cursor (scene linear)",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0),
    )

    max: FloatVectorProperty(
        name="Maximum",
        description="Brightest color in sampled area (scene linear)",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0)
    )

    min: FloatVectorProperty(
        name="Minimum",
        description="Darkest color in sampled area (scene linear)",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(0.0, 0.0, 0.0)
    )

    median: FloatVectorProperty(
        name="Median",
        description="Median color of sampled area (scene linear)",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(0.5, 0.5, 0.5)
    )
