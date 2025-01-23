# LAB_properties.py
import bpy
from bpy.props import FloatProperty, BoolProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraideLABProperties(PropertyGroup):
   suppress_updates: BoolProperty(default=False)
   
   def update_lab_values(self, context):
       if is_updating() or self.suppress_updates:
           return
       lab_values = (self.lightness, self.a, self.b)
       sync_all(context, 'lab', lab_values)

   lightness: FloatProperty(
       name="L",
       min=0.0,
       max=100.0, 
       default=50.0,
       update=update_lab_values
   )
   
   a: FloatProperty(
       name="a",
       min=-128.0,
       max=127.0,
       default=0.0,
       update=update_lab_values
   )
   
   b: FloatProperty( 
       name="b",
       min=-128.0,
       max=127.0,
       default=0.0,
       update=update_lab_values
   )