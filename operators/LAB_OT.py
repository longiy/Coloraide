# LAB_OT.py 
import bpy
from bpy.types import Operator
from ..COLORAIDE_utils import rgb_to_hsv
from ..COLORAIDE_sync import sync_all, is_updating

class COLOR_OT_sync_lab(Operator):
    bl_idname = "color.sync_lab"
    bl_label = "Sync LAB Values"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        if is_updating():
            return {'FINISHED'}
        current_color = tuple(context.window_manager.coloraide_picker.mean)
        lab_values = rgb_to_lab(current_color)
        sync_all(context, 'lab', lab_values)
        return {'FINISHED'}