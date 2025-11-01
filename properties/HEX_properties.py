"""
Hex color property definitions for Coloraide addon - Blender 5.0+
Uses colorspace module for proper sRGB <-> scene linear conversion.
"""

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraideHexProperties(PropertyGroup):
    """
    Properties for hex color input.
    Hex values are inherently sRGB and are converted to scene linear internally.
    """
    
    suppress_updates: BoolProperty(default=False)
    
    def update_hex_value(self, context):
        """Handle hex color updates and validation."""
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
            
        # Sync with hex string (sync_all will convert to linear via 'hex' source)
        try:
            sync_all(context, 'hex', value)
        except Exception as e:
            print(f"Error updating hex color: {e}")
            # Reset to previous valid value on error
            if hasattr(self, '_prev_value'):
                self.suppress_updates = True
                self.value = self._prev_value
                self.suppress_updates = False

    value: StringProperty(
        name="Hex",
        description="Color in hex format (sRGB, e.g. #FF0000)",
        default="#808080",
        maxlen=7,
        update=update_hex_value
    )
