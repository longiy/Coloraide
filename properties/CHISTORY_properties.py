import bpy
from bpy.props import IntProperty, FloatVectorProperty, BoolProperty, CollectionProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColorHistoryItemProperties(PropertyGroup):
    """Individual color history item with optimized update handling"""
    suppress_updates: BoolProperty(default=False)
    
    def update_history_color(self, context):
        """Update handler with improved sync check"""
        if is_updating() or self.suppress_updates:
            return
        sync_all(context, 'history', self.color)
            
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        default=(0.0, 0.0, 0.0),
        update=update_history_color
    )


class ColoraideHistoryProperties(PropertyGroup):
    """
    Color history management with O(1) duplicate checking.
    
    OPTIMIZATION: Uses Python set for instant duplicate detection
    instead of O(n) linear search through all items.
    """
    size: IntProperty(
        default=8,
        min=8,
        max=80
    )
    
    items: CollectionProperty(
        type=ColorHistoryItemProperties
    )
    
    # NEW: Set for O(1) duplicate checking
    _color_hashes: set = set()  # Not a Blender property, pure Python
    
    def reset_all_suppress_flags(self):
        """Reset suppress_updates flag on all history items"""
        for item in self.items:
            item.suppress_updates = False
    
    def _hash_color(self, color):
        """Create hashable representation of color with tolerance"""
        # Round to 4 decimals for fuzzy matching
        return tuple(round(c, 4) for c in color[:3])
    
    def initialize_history(self):
        """Initialize history with optimized clearing"""
        items = self.items
        
        # Clear hash set
        self._color_hashes = set()
        
        # Efficient batch removal
        while items:
            items.remove(0)
            
        # Batch add initial items
        for _ in range(self.size):
            item = items.add()
            item.suppress_updates = True
            item.color = (0.0, 0.0, 0.0)
            item.suppress_updates = False
        
        # Add default color to hash set
        self._color_hashes.add(self._hash_color((0.0, 0.0, 0.0)))
        
        # Double-check all flags are reset
        self.reset_all_suppress_flags()

    def add_color(self, color):
        """
        Add color to history with O(1) duplicate checking.
        
        OLD: O(n) - loop through all items comparing colors
        NEW: O(1) - set lookup
        
        Performance: 80 items * 3 comparisons = 240 ops → 1 hash lookup
        """
        if not color or not all(isinstance(c, float) for c in color):
            return
        
        # O(1) duplicate check using set
        color_hash = self._hash_color(color)
        if color_hash in self._color_hashes:
            return  # Already exists
        
        items = self.items
        
        # Remove last item if at size limit
        if len(items) >= self.size:
            removed_item = items[-1]
            removed_hash = self._hash_color(removed_item.color)
            self._color_hashes.discard(removed_hash)
            items.remove(len(items) - 1)
        
        # Add new color at beginning
        item = items.add()
        item.suppress_updates = True
        item.color = color
        
        # Efficient batch move to front
        items.move(len(items) - 1, 0)
        
        # Add to hash set
        self._color_hashes.add(color_hash)
        
        # Reset flag
        item.suppress_updates = False
        
        # Double-check all flags are reset
        self.reset_all_suppress_flags()
    
    def get_color_at_index(self, index):
        """Safely get color at specific index"""
        if 0 <= index < len(self.items):
            return self.items[index].color
        return None