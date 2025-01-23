import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraideRGBProperties(PropertyGroup):
    suppress_updates: BoolProperty(default=False)
    
    def update_rgb_values(self, context):
        if is_updating() or self.suppress_updates:
            return
        rgb_bytes = (self.red, self.green, self.blue)
        sync_all(context, 'rgb', rgb_bytes)

    red: IntProperty(
        name="R",
        min=0,
        max=255,
        default=128,
        update=update_rgb_values
    )
    
    green: IntProperty(
        name="G",
        min=0,
        max=255,
        default=128,
        update=update_rgb_values
    )
    
    blue: IntProperty(
        name="B", 
        min=0,
        max=255,
        default=128,
        update=update_rgb_values
    )
    
    alpha: FloatProperty(
        name="A",
        min=0.0,
        max=1.0,
        default=1.0,
        precision=3
    )