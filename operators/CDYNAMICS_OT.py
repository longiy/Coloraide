"""
Operator for applying random color variations during brush strokes.
"""

import bpy
import random
from bpy.types import Operator
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating, UpdateFlags

def apply_color_variation(original_color, strength):
    """Apply random color variation to a brush color"""
    if strength <= 0:
        return original_color
    
    random_color = (random.random(), random.random(), random.random())
    strength_factor = strength / 100.0
    
    return tuple(
        original + (random - original) * strength_factor
        for original, random in zip(original_color, random_color)
    )

def is_mouse_in_ui(context, event):
    """Check if mouse is over any UI regions"""
    if not context.area:
        return False
        
    x, y = event.mouse_x, event.mouse_y
    
    for region in context.area.regions:
        if region.type in {'TOOLS', 'UI', 'HEADER', 'TOOL_HEADER', 'NAV_BAR', 'TOOL_PROPS'}:
            if (region.x <= x <= region.x + region.width and 
                region.y <= y <= region.y + region.height):
                return True
    return False

class BRUSH_OT_reset_dynamics(bpy.types.Operator):
    bl_idname = "brush.reset_dynamics"
    bl_label = "Reset Dynamics"
    bl_description = "Reset color dynamics settings to default"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        dynamics = context.window_manager.coloraide_dynamics
        dynamics.strength = 0
        dynamics.running = False
        return {'FINISHED'}

class BRUSH_OT_color_dynamics(Operator):
    """Apply random color variations during brush strokes"""
    bl_idname = "brush.color_dynamics"
    bl_label = "Color Dynamics"
    bl_description = "Apply random color variation during brush strokes"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.coloraide_dynamics.strength > 0

    def modal(self, context, event):
        wm = context.window_manager
        dynamics = wm.coloraide_dynamics
        
        if not dynamics.strength:
            self.cleanup(context)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            mouse_in_ui = is_mouse_in_ui(context, event)
            
            if mouse_in_ui:
                return {'PASS_THROUGH'}
            
            base_color = tuple(wm.coloraide_picker.mean)
            
            if event.value == 'PRESS':
                # Generate new random color
                if not is_updating('dynamics'):
                    new_color = apply_color_variation(
                        base_color,
                        dynamics.strength
                    )
                    sync_all(context, 'dynamics', new_color)
                    
            elif event.value == 'RELEASE':
                # Restore original color
                if not is_updating('dynamics'):
                    sync_all(context, 'dynamics', base_color)

        return {'PASS_THROUGH'}

    def cleanup(self, context):
        """Reset state and colors"""
        wm = context.window_manager
        wm.coloraide_dynamics.running = False
        
        # Restore base color
        if not is_updating('dynamics'):
            base_color = tuple(wm.coloraide_picker.mean)
            sync_all(context, 'dynamics', base_color)

    def invoke(self, context, event):
        wm = context.window_manager
        wm.modal_handler_add(self)
        wm.coloraide_dynamics.running = True
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(BRUSH_OT_color_dynamics)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_color_dynamics)