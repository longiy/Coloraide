import bpy
from bpy.props import IntProperty, FloatVectorProperty, BoolProperty, CollectionProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColorHistoryItemProperties(PropertyGroup):
    """Individual color history item with optimized update handling"""
    suppress_updates: BoolProperty(default=False)
    
    def reset_all_suppress_flags(self):
        """Reset suppress_updates flag on all history items"""
        print("Resetting all suppress_updates flags")
        for item in self.items:
            item.suppress_updates = False
    
    def update_history_color(self, context):
        """Update handler with improved sync check"""
        print(f"\n=== COLOR HISTORY ITEM CLICKED ===")
        print(f"Selected color: {self.color}")
        
        # Add more detailed debugging
        from ..COLORAIDE_sync import _UPDATING, _UPDATE_SOURCE
        print(f"Global _UPDATING state: {_UPDATING}")
        print(f"Global _UPDATE_SOURCE: {_UPDATE_SOURCE}")
        print(f"self.suppress_updates: {self.suppress_updates}")
        
        if is_updating():
            print("is_updating() returned True")
            if _UPDATE_SOURCE:
                print(f"Update is coming from source: {_UPDATE_SOURCE}")
            return
        
        if self.suppress_updates:
            print("self.suppress_updates is True")
            return
            
        print("Calling sync_all with color:", self.color)
        sync_all(context, 'history', self.color)
        print("After sync_all call")
            
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
    
    def reset_all_suppress_flags(self):
        """Reset suppress_updates flag on all history items"""
        print("Resetting all suppress_updates flags")
        for item in self.items:
            item.suppress_updates = False
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
            item.suppress_updates = False  # Make sure to reset flag

        # Double-check all flags are reset
        self.reset_all_suppress_flags()

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
        
        # Make sure to reset the flag
        item.suppress_updates = False
        
        # Double-check all flags are reset
        self.reset_all_suppress_flags()
        
    def get_color_at_index(self, index):
        """Safely get color at specific index"""
        if 0 <= index < len(self.items):
            return self.items[index].color
        return None