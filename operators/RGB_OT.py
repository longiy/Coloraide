"""
Operator for handling RGB color updates and synchronization.
"""

import bpy
from bpy.types import Operator
from ..properties.RGB_properties import sync_rgb_from_brush
from ..COLORAIDE_utils import is_updating

class COLOR_OT_sync_rgb(Operator):
    """Operator to sync RGB values with current color"""
    bl_idname = "color.sync_rgb"
    bl_label = "Sync RGB Values"
    bl_description = "Synchronize RGB sliders with current color"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return hasattr(context.window_manager, 'coloraide_rgb')
    
    def execute(self, context):
        if not is_updating('rgb'):
            current_color = tuple(context.window_manager.coloraide_picker.mean)
            sync_rgb_from_brush(context, current_color)
        return {'FINISHED'}