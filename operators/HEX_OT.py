import bpy
from bpy.types import Operator
from ..COLORAIDE_sync import sync_all, is_updating

class COLOR_OT_sync_hex(Operator):
    bl_idname = "color.sync_hex"
    bl_label = "Sync Hex Value"
    bl_description = "Synchronize hex value with current color"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        if is_updating():
            return {'FINISHED'}
        current_color = tuple(context.window_manager.coloraide_picker.mean)
        rgb_bytes = tuple(int(c * 255) for c in current_color)
        hex_value = "#{:02X}{:02X}{:02X}".format(*rgb_bytes)
        sync_all(context, 'hex', hex_value)
        return {'FINISHED'}