import bpy
from bpy.props import FloatProperty, FloatVectorProperty, BoolProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraideWheelProperties(PropertyGroup):
    suppress_updates: BoolProperty(default=False)
    
    def update_wheel_color(self, context):
        if is_updating() or self.suppress_updates:
            return
        color = tuple(self.color[:3])
        sync_all(context, 'wheel', color)

    scale: FloatProperty(
        name="Wheel Size",
        min=1.0,
        max=3.0,
        default=1.5
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