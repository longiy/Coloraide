"""
Operators for handling hex color updates and validation.
"""

import bpy
from bpy.types import Operator
from ..properties.HEX_properties import sync_hex_from_rgb
from ..COLORAIDE_utils import is_updating

class COLOR_OT_sync_hex(Operator):
    """Operator to sync hex value with current color"""
    bl_idname = "color.sync_hex"
    bl_label = "Sync Hex Value"
    bl_description = "Synchronize hex value with current color"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return hasattr(context.window_manager, 'coloraide_hex')
    
    def execute(self, context):
        if not is_updating('hex'):
            current_color = tuple(context.window_manager.coloraide_picker.mean)
            sync_hex_from_rgb(context, current_color)
        return {'FINISHED'}

class COLOR_OT_validate_hex(Operator):
    """Operator to validate and format hex input"""
    bl_idname = "color.validate_hex"
    bl_label = "Validate Hex"
    bl_description = "Validate and format hex color value"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        hex_props = context.window_manager.coloraide_hex
        value = hex_props.value.strip().upper()
        
        # Add # if missing
        if not value.startswith('#'):
            value = '#' + value
            
        # Validate length
        if len(value) > 7:
            value = value[:7]
        
        # Validate characters
        valid_chars = set('0123456789ABCDEF#')
        if not all(c in valid_chars for c in value):
            self.report({'WARNING'}, "Invalid hex color format")
            value = '#000000'
            
        # Pad with zeros if incomplete
        if len(value) < 7:
            value = value.ljust(7, '0')
            
        hex_props.value = value
        return {'FINISHED'}