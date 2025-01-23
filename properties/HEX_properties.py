"""
Hex color input properties with synchronization using central sync system.
"""

import bpy
from bpy.props import StringProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import UpdateFlags, is_updating

def update_hex_value(self, context):
    """Update handler for hex color changes"""
    if is_updating('hex'):
        return
        
    # First validate the hex value
    value = self.value.strip().upper()
    if not value.startswith('#'):
        value = '#' + value
        
    # Clean and format hex string
    value = ''.join(c for c in value if c in '0123456789ABCDEF#')
    if len(value) > 7:
        value = value[:7]
    elif len(value) < 7:
        value = value.ljust(7, '0')
        
    # Only update if validation changed the value
    if value != self.value:
        self.value = value
        return
        
    sync_all(context, 'hex', self.value)

class ColoraideHexProperties(PropertyGroup):
    """Properties for hex color input"""
    
    value: StringProperty(
        name="Hex",
        description="Color in hex format (e.g. #FF0000)",
        default="#808080",
        maxlen=7,
        update=update_hex_value
    )