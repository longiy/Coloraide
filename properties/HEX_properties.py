"""
Hex color input properties with bidirectional synchronization.
"""

import bpy
from bpy.props import StringProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_utils import (
    hex_to_rgb,
    rgb_to_hex,
    UpdateFlags
)

def sync_hex_from_rgb(context, rgb_color):
    """
    Synchronize hex value from RGB color.
    
    Args:
        context: Blender context
        rgb_color: Tuple of RGB values (0-1)
    """
    with UpdateFlags('hex'):
        wm = context.window_manager
        if hasattr(wm, 'coloraide_hex'):
            # Use the rgb_to_hex function from COLORAIDE_utils
            wm.coloraide_hex.value = rgb_to_hex(rgb_color)

def validate_hex_string(self, value):
    """Validate and format hex color value"""
    value = value.strip().upper()
    if not value.startswith('#'):
        value = '#' + value
    value = ''.join(c for c in value if c in '0123456789ABCDEF#')
    if len(value) > 7:
        value = value[:7]
    elif len(value) < 7:
        value = value.ljust(7, '0')
    return value

def update_from_hex(self, context):
    """Update handler for hex color changes"""
    with UpdateFlags('hex'):
        hex_str = self.value.lstrip('#')
        if len(hex_str) == 6:
            try:
                # Use the hex_to_rgb function from COLORAIDE_utils
                rgb_float = hex_to_rgb(self.value)
                # Update picker.mean (will trigger sync of other inputs)
                picker = context.window_manager.coloraide_picker
                picker.mean = rgb_float
            except ValueError:
                pass

class ColoraideHexProperties(PropertyGroup):
    """Properties for hex color input"""
    
    value: StringProperty(
        name="Hex",
        description="Color in hex format (e.g. #FF0000)",
        default="#808080",
        maxlen=7,
        update=update_from_hex,
        set=validate_hex_string
    )