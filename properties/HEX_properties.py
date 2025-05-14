"""
Hex color property definitions for Coloraide addon.
"""

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating
from ..COLORAIDE_utils import hex_to_rgb

class ColoraideHexProperties(PropertyGroup):
    """Properties for hex color input"""
    
    suppress_updates: BoolProperty(default=False)
    
    def update_hex_value(self, context):
        """Handle hex color updates and validation"""
        if is_updating() or self.suppress_updates:
            return
            
        # Clean and validate hex format
        value = self.value.strip().upper()
        
        # Add # prefix if missing
        if not value.startswith('#'):
            value = '#' + value
            
        # Validate hex format
        if len(value) != 7 or not all(c in '0123456789ABCDEF#' for c in value):
            # Invalid hex - reset to previous valid value or default
            if hasattr(self, '_prev_value'):
                self.suppress_updates = True
                self.value = self._prev_value
                self.suppress_updates = False
            else:
                self.suppress_updates = True
                self.value = '#808080'
                self.suppress_updates = False
            return
            
        # Store valid value
        self._prev_value = value
            
        # # Only update if format changed
        # if value != self.value:
        #     self.suppress_updates = True
        #     self.value = value
        #     self.suppress_updates = False
        #     return
            
        # Convert hex to RGB and sync
        try:
            rgb_float = hex_to_rgb(value)
            sync_all(context, 'hex', rgb_float)
        except Exception as e:
            print(f"Error updating hex color: {e}")
            # Reset to previous valid value on error
            if hasattr(self, '_prev_value'):
                self.suppress_updates = True
                self.value = self._prev_value
                self.suppress_updates = False

    value: StringProperty(
        name="Hex",
        description="Color in hex format (e.g. #FF0000)",
        default="#808080",
        maxlen=7,
        update=update_hex_value
    )