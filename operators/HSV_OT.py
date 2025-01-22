"""
Operator for handling HSV color updates and synchronization.
"""

import bpy
from bpy.types import Operator
from ..properties.HSV_properties import sync_hsv_from_rgb
from ..COLORAIDE_utils import is_updating  # Changed import

class COLOR_OT_sync_hsv(Operator):
    """Operator to sync HSV values with current color"""
    bl_idname = "color.sync_hsv"
    bl_label = "Sync HSV Values"
    bl_description = "Synchronize HSV sliders with current color"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return hasattr(context.window_manager, 'coloraide_hsv')
    
    def execute(self, context):
        if not is_updating('hsv'):  # Changed check
            current_color = tuple(context.window_manager.coloraide_picker.mean)
            sync_hsv_from_rgb(context, current_color)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(COLOR_OT_sync_hsv)

def unregister():
    bpy.utils.unregister_class(COLOR_OT_sync_hsv)