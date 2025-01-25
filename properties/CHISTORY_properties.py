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
        subtype='COLOR',  # Changed from COLOR_GAMMA to COLOR
        size=3,
        min=0.0, max=1.0,
        default=(0.0, 0.0, 0.0),
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
    
    def initialize_history(self):
        # Clear existing items
        while len(self.items) > 0:
            self.items.remove(0)
            
        # Add initial items up to size
        for _ in range(self.size):
            item = self.items.add()
            item.suppress_updates = True
            item.color = (0.0, 0.0, 0.0)
            item.suppress_updates = False

    def add_color(self, color):
        # Check for duplicate colors
        for item in self.items:
            if all(abs(a - b) < 0.001 for a, b in zip(item.color, color)):
                return
                
        # Create new color at beginning
        new_item = self.items.add()
        new_item.suppress_updates = True
        new_item.color = color
        new_item.suppress_updates = False
        
        # Remove excess colors
        while len(self.items) > self.size:
            self.items.remove(len(self.items) - 1)
            
        # Move new color to front
        for i in range(len(self.items) - 1, 0, -1):
            self.items.move(i, i - 1)