import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, FloatVectorProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraideRGBProperties(PropertyGroup):
    suppress_updates: BoolProperty(default=False)
    
    def update_rgb_values(self, context):
        if is_updating() or self.suppress_updates:
            return
        
        # Update the stored preview colors (like history does)
        self.red_preview = (self.red / 255.0, 0.0, 0.0)
        self.green_preview = (0.0, self.green / 255.0, 0.0)
        self.blue_preview = (0.0, 0.0, self.blue / 255.0)
        
        rgb_bytes = (self.red, self.green, self.blue)
        # Use RELATIVE mode for slider adjustments
        sync_all(context, 'rgb', rgb_bytes, mode='relative')

    red: IntProperty(
        name="R",
        min=0,
        max=255,
        default=128,
        update=update_rgb_values
    )
    
    green: IntProperty(
        name="G",
        min=0,
        max=255,
        default=128,
        update=update_rgb_values
    )
    
    blue: IntProperty(
        name="B", 
        min=0,
        max=255,
        default=128,
        update=update_rgb_values
    )
    
    alpha: FloatProperty(
        name="A",
        min=0.0,
        max=1.0,
        default=1.0,
        precision=3
    )
    
    # Stored preview properties (exactly like color history)
    red_preview: FloatVectorProperty(
        name="Red Preview",
        subtype='COLOR_GAMMA',  # Same as history
        size=3,
        min=0.0, max=1.0,
        default=(0.5, 0.0, 0.0)  # Default pure red
        # No get= callback, no update= callback - just stored values
    )
    
    green_preview: FloatVectorProperty(
        name="Green Preview",
        subtype='COLOR_GAMMA',  # Same as history
        size=3,
        min=0.0, max=1.0,
        default=(0.0, 0.5, 0.0)  # Default pure green
    )
    
    blue_preview: FloatVectorProperty(
        name="Blue Preview",
        subtype='COLOR_GAMMA',  # Same as history
        size=3,
        min=0.0, max=1.0,
        default=(0.0, 0.0, 0.5)  # Default pure blue
    )