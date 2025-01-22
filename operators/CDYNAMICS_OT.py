"""
Operator for applying random color variations during brush strokes.
"""

import bpy
import random
from bpy.types import Operator
from ..properties.CDYNAMICS_properties import ColoraideDynamicsProperties

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

class BRUSH_OT_color_dynamics(Operator):
    """Apply random color variations during brush strokes"""
    bl_idname = "brush.color_dynamics"
    bl_label = "Color Dynamics"
    bl_description = "Apply random color variation during brush strokes"
    bl_options = {'REGISTER'}
    
    @classmethod
    def poll(cls, context):
        return context.window_manager.coloraide_dynamics.strength > 0
    
    def update_brush_colors(self, context, color):
        """Update brush colors with the provided color"""
        ts = context.tool_settings
        
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = color
            
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = color
    
    def modal(self, context, event):
        wm = context.window_manager
        dynamics = wm.coloraide_dynamics
        
        # Check if dynamics should be turned off
        if not dynamics.strength:
            self.cleanup(context)
            return {'CANCELLED'}
        
        if event.type == 'LEFTMOUSE':
            mouse_in_ui = is_mouse_in_ui(context, event)
            
            # Handle UI clicks normally
            if mouse_in_ui:
                return {'PASS_THROUGH'}
            
            # Apply color dynamics for non-UI clicks
            if not mouse_in_ui:
                base_color = dynamics.get_base_color(context)
                
                if event.value == 'PRESS':
                    # Generate new random color on press
                    new_color = apply_color_variation(
                        base_color,
                        dynamics.strength
                    )
                    self.update_brush_colors(context, new_color)
                    
                elif event.value == 'RELEASE':
                    # Restore base color on release
                    self.update_brush_colors(context, base_color)
        
        return {'PASS_THROUGH'}
    
    def cleanup(self, context):
        """Reset state and colors"""
        wm = context.window_manager
        dynamics = wm.coloraide_dynamics
        dynamics.running = False
        
        # Restore base color
        base_color = dynamics.get_base_color(context)
        self.update_brush_colors(context, base_color)
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.modal_handler_add(self)
        wm.coloraide_dynamics.running = True
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(BRUSH_OT_color_dynamics)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_color_dynamics)