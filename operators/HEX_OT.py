"""
Operator for synchronizing hex color values.
"""

import bpy
from bpy.types import Operator
from ..COLORAIDE_sync import sync_all, is_updating
from ..COLORAIDE_colorspace import rgb_to_hex

class COLOR_OT_sync_hex(Operator):
    bl_idname = "color.sync_hex"
    bl_label = "Sync Hex Value"
    bl_description = "Synchronize hex value with current color"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return hasattr(context.window_manager, 'coloraide_hex')
    
    def execute(self, context):
        if is_updating():
            return {'FINISHED'}
            
        # Get current RGB color and sync
        current_color = tuple(context.window_manager.coloraide_picker.mean)
        sync_all(context, 'hex', current_color)
        return {'FINISHED'}