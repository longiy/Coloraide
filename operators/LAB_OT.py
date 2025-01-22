"""
Operator for handling LAB color updates and synchronization.
"""

import bpy
from bpy.types import Operator
from ..properties.LAB_properties import sync_lab_from_rgb
from ..COLORAIDE_utils import is_updating

class COLOR_OT_sync_lab(Operator):
    """Operator to sync LAB values with current color"""
    bl_idname = "color.sync_lab"
    bl_label = "Sync LAB Values"
    bl_description = "Synchronize LAB sliders with current color"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return hasattr(context.window_manager, 'coloraide_lab')
    
    def execute(self, context):
        if not is_updating('lab'):
            current_color = tuple(context.window_manager.coloraide_picker.mean)
            sync_lab_from_rgb(context, current_color)
        return {'FINISHED'}