# HSV_OT.py
import bpy
from bpy.types import Operator
from ..COLORAIDE_utils import rgb_to_hsv
from ..COLORAIDE_sync import sync_all, is_updating

class COLOR_OT_sync_hsv(Operator):
    bl_idname = "color.sync_hsv"
    bl_label = "Sync HSV Values"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        if is_updating():
            return {'FINISHED'}
        current_color = tuple(context.window_manager.coloraide_picker.mean)
        hsv_values = rgb_to_hsv(current_color)
        hsv_display = (hsv_values[0]*360.0, hsv_values[1]*100.0, hsv_values[2]*100.0)
        sync_all(context, 'hsv', hsv_display)
        return {'FINISHED'}