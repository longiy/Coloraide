"""
Operator for selecting colors from history with priority handling.
"""

import bpy
from bpy.props import FloatVectorProperty
from bpy.types import Operator
from ..COLORAIDE_brush_sync import update_brush_color, set_history_update_flag

class COLOR_OT_use_history_color(Operator):
    """Select a color from history with priority handling"""
    bl_idname = "color.use_history_color"
    bl_label = "Use History Color"
    bl_description = "Set the current color from history (high priority)"
    bl_options = {'REGISTER', 'UNDO'}
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(0.0, 0.0, 0.0)
    )
    
    def execute(self, context):
        # Set flag to indicate this is a high-priority history update
        set_history_update_flag(True)
        try:
            # Update brush color with priority
            update_brush_color(context, self.color, from_history=True)
            
            # Move this color to the front of history
            context.window_manager.coloraide_history.add_color(self.color)
        finally:
            # Always reset the flag when done
            set_history_update_flag(False)
            
        return {'FINISHED'}

def register():
    bpy.utils.register_class(COLOR_OT_use_history_color)

def unregister():
    bpy.utils.unregister_class(COLOR_OT_use_history_color)