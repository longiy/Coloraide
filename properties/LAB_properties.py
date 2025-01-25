"""LAB Properties with fast response"""

import bpy
from bpy.props import FloatProperty, BoolProperty
from bpy.types import PropertyGroup
from .. import COLORAIDE_sync
from .. import COLORAIDE_utils

class ColoraideLABProperties(PropertyGroup):
    suppress_updates: BoolProperty(default=False)
    
    def update_lab_values(self, context):
        if COLORAIDE_sync.is_updating() or self.suppress_updates:
            return
        lab_values = (self.lightness, self.a, self.b)
        COLORAIDE_sync.sync_all(context, 'lab', lab_values)

    lightness: FloatProperty(
        name="L",
        min=0.0,
        max=100.0,
        default=50.0,
        precision=0,
        step=100,
        update=update_lab_values
    )
    
    a: FloatProperty(
        name="a",
        min=-128.0,
        max=127.0,
        default=0.0,
        precision=0,
        step=100,
        update=update_lab_values
    )
    
    b: FloatProperty(
        name="b",
        min=-128.0,
        max=127.0,
        default=0.0,
        precision=0,
        step=100,
        update=update_lab_values
    )