# CHISTORY_properties.py
import bpy
from bpy.props import IntProperty, FloatVectorProperty, BoolProperty, CollectionProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColorHistoryItemProperties(PropertyGroup):
   suppress_updates: BoolProperty(default=False)
   
   def update_history_color(self, context):
       if is_updating() or self.suppress_updates:
           return
       sync_all(context, 'history', self.color)
           
   color: FloatVectorProperty(
       name="Color",
       subtype='COLOR_GAMMA',
       size=3,
       min=0.0, max=1.0,
       default=(1.0, 1.0, 1.0),
       update=update_history_color
   )

class ColoraideHistoryProperties(PropertyGroup):
   size: IntProperty(
       default=8,
       min=8,
       max=80
   )
   items: CollectionProperty(
       type=ColorHistoryItemProperties
   )

   def add_color(self, color):
       for item in self.items:
           if tuple(item.color) == tuple(color):
               return
               
       if len(self.items) >= self.size:
           self.items.remove(len(self.items) - 1)
           
       new_item = self.items.add()
       new_item.suppress_updates = True
       new_item.color = color
       new_item.suppress_updates = False

       for i in range(len(self.items) - 1, 0, -1):
           self.items.move(i, i - 1)