"""
LAB color property definitions for Coloraide addon.
"""

import bpy
from bpy.props import FloatProperty, BoolProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating
from ..COLORAIDE_utils import rgb_to_lab, lab_to_rgb

class ColoraideLABProperties(PropertyGroup):
    """Properties for LAB color control"""
    
    suppress_updates: BoolProperty(default=False)
    
    def update_lab_values(self, context):
        """Update handler for LAB slider changes"""
        if is_updating() or self.suppress_updates:
            return
            
        # Get current LAB values
        current_lab = (self.lightness, self.a, self.b)
        
        # Convert to RGB and sync
        try:
            rgb_color = lab_to_rgb(current_lab)
            sync_all(context, 'lab', current_lab)
        except Exception as e:
            print(f"Error updating LAB values: {e}")

    lightness: FloatProperty(
        name="L",
        description="Lightness (0-100)",
        min=0.0,
        max=100.0,
        default=50.0,
        precision=2,
        update=update_lab_values
    )
    
    a: FloatProperty(
        name="a",
        description="Green (-) to Red (+)",
        min=-128.0,
        max=127.0,
        default=0.0,
        precision=2,
        update=update_lab_values
    )
    
    b: FloatProperty(
        name="b",
        description="Blue (-) to Yellow (+)",
        min=-128.0,
        max=127.0,
        default=0.0,
        precision=2,
        update=update_lab_values
    )