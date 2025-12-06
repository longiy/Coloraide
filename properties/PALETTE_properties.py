# PALETTE_properties.py
import bpy
from bpy.props import BoolProperty, FloatVectorProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraidePaletteProperties(PropertyGroup):
   suppress_updates: BoolProperty(default=False)
   
   # REMOVED: update_preview_color callback
   # This was causing recursion because it would call sync_all('palette')
   # whenever the preview_color was updated by sync_all() itself
   
   preview_color: FloatVectorProperty(
       subtype='COLOR_GAMMA',
       size=3,
       min=0.0, max=1.0,
       default=(1.0, 1.0, 1.0),
       # NO UPDATE CALLBACK - preview_color is display-only
   )