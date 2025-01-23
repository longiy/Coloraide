"""Operator for RGB synchronization"""

import bpy
from bpy.types import Operator
from ..COLORAIDE_sync import sync_all, is_updating

class COLOR_OT_sync_rgb(Operator):
    bl_idname = "color.sync_rgb"
    bl_label = "Sync RGB Values"
    bl_description = "Synchronize RGB sliders with current color"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return hasattr(context.window_manager, 'coloraide_rgb')
    
    def execute(self, context):
        if is_updating():
            return {'FINISHED'}
            
        current_color = tuple(context.window_manager.coloraide_picker.mean)
        rgb_bytes = tuple(int(c * 255) for c in current_color)
        sync_all(context, 'rgb', rgb_bytes)
        return {'FINISHED'}