# CHISTORY_OT.py
# CLEANED: Removed COLOR_OT_reset_history_flags (debugging operator)

import bpy
from bpy.types import Operator
from ..COLORAIDE_sync import sync_all, is_updating

class COLOR_OT_adjust_history_size(Operator):
    bl_idname = "color.adjust_history_size"
    bl_label = "Adjust History Size"
    bl_options = {'INTERNAL'}
    
    increase: bpy.props.BoolProperty()
    
    def execute(self, context):
        history = context.window_manager.coloraide_history
        if self.increase and history.size < 80:
            history.size += 1
        elif not self.increase and history.size > 8:
            history.size -= 1
        return {'FINISHED'}


class COLOR_OT_clear_history(Operator):
    bl_idname = "color.clear_history"
    bl_label = "Clear History"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        history = context.window_manager.coloraide_history
        while len(history.items) > 0:
            history.items.remove(0)
        return {'FINISHED'}