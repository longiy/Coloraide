"""
Operators for handling color wheel updates and interactions.
"""

import bpy
from bpy.types import Operator
from ..COLORAIDE_sync import sync_all, is_updating

class COLOR_OT_sync_wheel(Operator):
    bl_idname = "color.sync_wheel"
    bl_label = "Sync Color Wheel"
    bl_description = "Synchronize color wheel with current color"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return hasattr(context.window_manager, 'coloraide_wheel')
    
    def execute(self, context):
        if is_updating():
            return {'FINISHED'}
        current_color = tuple(context.window_manager.coloraide_picker.mean)
        sync_all(context, 'wheel', current_color)
        return {'FINISHED'}

class COLOR_OT_reset_wheel_scale(Operator):
    """Operator to reset the color wheel scale"""
    bl_idname = "color.reset_wheel_scale"
    bl_label = "Reset Wheel Scale"
    bl_description = "Reset the color wheel size to default"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return hasattr(context.window_manager, 'coloraide_wheel')
    
    def execute(self, context):
        context.window_manager.coloraide_wheel.scale = 1.5
        return {'FINISHED'}

def register():
    bpy.utils.register_class(COLOR_OT_sync_wheel)
    bpy.utils.register_class(COLOR_OT_reset_wheel_scale)

def unregister():
    bpy.utils.unregister_class(COLOR_OT_reset_wheel_scale)
    bpy.utils.unregister_class(COLOR_OT_sync_wheel)