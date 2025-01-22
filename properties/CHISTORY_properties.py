"""
Standalone property definitions for color history management.
"""

import bpy
from bpy.props import IntProperty, FloatVectorProperty, CollectionProperty
from bpy.types import PropertyGroup

class ColorHistoryItemProperties(PropertyGroup):
    """Individual color history item properties"""
    
    def update_color(self, context):
        """Update handler for when a history color is selected"""
        wm = context.window_manager
        # Update picker colors
        wm.coloraide_picker.mean = self.color
        wm.coloraide_picker.current = self.color
        
        # Update brush colors
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = self.color
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = self.color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = self.color
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_color
    )

class ColoraideHistoryProperties(PropertyGroup):
    """Properties for color history management"""
    
    size: IntProperty(
        name="History Size",
        description="Number of color history slots",
        default=8,
        min=8,
        max=80
    )
    
    items: CollectionProperty(
        type=ColorHistoryItemProperties,
        name="Color History",
        description="History of recently picked colors"
    )

    def initialize_history(self):
        """Initialize empty history slots"""
        for _ in range(self.size):
            self.items.add()
    
    def add_color(self, color):
        """Add a new color to history, avoiding duplicates"""
        # Check for duplicate
        for item in self.items:
            if (abs(item.color[0] - color[0]) < 0.001 and 
                abs(item.color[1] - color[1]) < 0.001 and 
                abs(item.color[2] - color[2]) < 0.001):
                return
        
        # Move all colors down
        for i in range(len(self.items) - 1, 0, -1):
            self.items[i].color = self.items[i-1].color
        
        # Add new color at start
        if len(self.items) > 0:
            self.items[0].color = color