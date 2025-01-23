# PALETTE_properties.py
import bpy
from bpy.props import BoolProperty, FloatVectorProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraidePaletteProperties(PropertyGroup):
   suppress_updates: BoolProperty(default=False)
   
   def update_preview_color(self, context):
       if is_updating() or self.suppress_updates:
           return
       sync_all(context, 'palette', self.preview_color)
   
   preview_color: FloatVectorProperty(
       subtype='COLOR_GAMMA',
       size=3,
       min=0.0, max=1.0,
       default=(1.0, 1.0, 1.0),
       update=update_preview_color
   )