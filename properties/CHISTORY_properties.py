import bpy
from bpy.props import IntProperty, FloatVectorProperty, BoolProperty, CollectionProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColorHistoryItemProperties(PropertyGroup):
    """Individual color history item with optimized update handling"""
    suppress_updates: BoolProperty(default=False)
    
    def update_history_color(self, context):
        """Update handler with priority overrides for history items"""
        if self.suppress_updates:
            return
            
        # Use 'history' as the source for priority sync
        sync_all(context, 'history', self.color)
            
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(0.0, 0.0, 0.0),
        update=update_history_color
    )

class ColoraideHistoryProperties(PropertyGroup):
    """Color history management with optimized operations"""
    size: IntProperty(
        default=8,
        min=8,
        max=80
    )
    
    items: CollectionProperty(
        type=ColorHistoryItemProperties
    )
    
    def initialize_history(self):
        """Initialize history with optimized clearing"""
        items = self.items
        # Efficient batch removal
        while items:
            items.remove(0)
            
        # Batch add initial items
        for _ in range(self.size):
            item = items.add()
            item.suppress_updates = True
            item.color = (0.0, 0.0, 0.0)
            item.suppress_updates = False

    def add_color(self, color):
        """Add color to history with optimized duplicate checking and shifting"""
        if not color or not all(isinstance(c, float) for c in color):
            return
            
        items = self.items
        
        # Quick duplicate check with early return
        for item in items:
            if all(abs(a - b) < 0.0001 for a, b in zip(item.color, color)):
                return
                
        # Remove last item if at size limit
        if len(items) >= self.size:
            items.remove(len(items) - 1)
            
        # Add new color at beginning
        item = items.add()
        item.suppress_updates = True
        item.color = color
        
        # Efficient batch move to front
        items.move(len(items) - 1, 0)
        item.suppress_updates = False
        
    def get_color_at_index(self, index):
        """Safely get color at specific index"""
        if 0 <= index < len(self.items):
            return self.items[index].color
        return None