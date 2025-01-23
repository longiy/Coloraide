"""
Operators for color history management.
"""

import bpy
from bpy.types import Operator
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating, UpdateFlags

class COLOR_OT_adjust_history_size(Operator):
    """Adjust the size of the color history"""
    bl_idname = "color.adjust_history_size"
    bl_label = "Adjust History Size"
    bl_description = "Add or remove color history slots"
    bl_options = {'INTERNAL'}
    
    increase: bpy.props.BoolProperty(
        name="Increase",
        description="Increase or decrease history size",
        default=True
    )
    
    @classmethod
    def description(cls, context, properties):
        if properties.increase:
            return "Add one more color slot (Maximum 80)"
        else:
            return "Remove one color slot (Minimum 8)"
    
    def execute(self, context):
        history = context.window_manager.coloraide_history
        
        # Increase size
        if self.increase and history.size < 80:
            history.size += 1
            
        # Decrease size
        elif not self.increase and history.size > 8:
            history.size -= 1
            
        return {'FINISHED'}

class COLOR_OT_clear_history(Operator):
    """Clear the entire color history"""
    bl_idname = "color.clear_history"
    bl_label = "Clear History"
    bl_description = "Clear all colors from history"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        history = context.window_manager.coloraide_history
        while len(history.items) > 0:
            history.items.remove(0)
        
        # Reinitialize empty slots
        for _ in range(history.size):
            history.items.add()
            
        return {'FINISHED'}

class COLOR_OT_remove_history_color(Operator):
    """Remove a specific color from history"""
    bl_idname = "color.remove_history_color"
    bl_label = "Remove Color"
    bl_description = "Remove this color from history"
    bl_options = {'INTERNAL'}
    
    index: bpy.props.IntProperty(
        name="Index",
        description="Index of color to remove",
        default=0,
        min=0
    )
    
    def execute(self, context):
        history = context.window_manager.coloraide_history
        if 0 <= self.index < len(history.items):
            history.items.remove(self.index)
            # Add empty slot at end to maintain size
            history.items.add()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(COLOR_OT_adjust_history_size)
    bpy.utils.register_class(COLOR_OT_clear_history)
    bpy.utils.register_class(COLOR_OT_remove_history_color)

def unregister():
    bpy.utils.unregister_class(COLOR_OT_remove_history_color)
    bpy.utils.unregister_class(COLOR_OT_clear_history)
    bpy.utils.unregister_class(COLOR_OT_adjust_history_size)