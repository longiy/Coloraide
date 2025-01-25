# HSV_properties.py
import bpy
from bpy.props import FloatProperty, BoolProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraideHSVProperties(PropertyGroup):
   suppress_updates: BoolProperty(default=False)
   
   def update_hsv_values(self, context):
       if is_updating() or self.suppress_updates:
           return
       hsv_values = (self.hue, self.saturation, self.value)
       sync_all(context, 'hsv', hsv_values)

   hue: FloatProperty(
       name="H",
       min=0.0,
       max=360.0,
       default=0.0,
       update=update_hsv_values,
       
   )
   
   saturation: FloatProperty(
       name="S", 
       min=0.0,
       max=100.0,
       default=0.0,
       subtype='PERCENTAGE',
       update=update_hsv_values
   )
   
   value: FloatProperty(
       name="V",
       min=0.0, 
       max=100.0,
       default=100.0,
       subtype='PERCENTAGE',
       update=update_hsv_values
   )