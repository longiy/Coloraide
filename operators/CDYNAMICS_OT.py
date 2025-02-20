# COLOR_OT_color_dynamics.py
import bpy
import random
from bpy.types import Operator
from ..COLORAIDE_sync import sync_all, is_updating
from ..COLORAIDE_brush_sync import update_brush_color

def apply_color_dynamics(original_color, strength):
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

class COLOR_OT_color_dynamics(Operator):
    bl_idname = "color.color_dynamics"
    bl_label = "Color Dynamics"
    bl_description = "Apply random color variation during brush strokes"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.coloraide_dynamics.strength > 0

    def invoke(self, context, event):
        wm = context.window_manager
        wm.coloraide_dynamics.base_color = tuple(wm.coloraide_picker.mean)  # Store initial color
        wm.modal_handler_add(self)
        wm.coloraide_dynamics.running = True
        return {'RUNNING_MODAL'}

# In COLOR_OT_color_dynamics.modal:

    def modal(self, context, event):
        wm = context.window_manager
        ts = context.tool_settings
        
        if not wm.coloraide_dynamics.strength:
            self.cleanup(context)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            mouse_in_ui = is_mouse_in_ui(context, event)
            
            if mouse_in_ui:
                return {'PASS_THROUGH'}
            
            if not mouse_in_ui:
                if event.value == 'PRESS':
                    base_color = tuple(wm.coloraide_picker.mean)
                    dynamic_color = apply_color_dynamics(
                        base_color,
                        wm.coloraide_dynamics.strength
                    )
                    
                    # Direct brush color modification without sync
                    if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
                        ts.gpencil_paint.brush.color = dynamic_color
                    if hasattr(ts, 'image_paint') and ts.image_paint.brush:
                        ts.image_paint.brush.color = dynamic_color
                        if ts.unified_paint_settings.use_unified_color:
                            ts.unified_paint_settings.color = dynamic_color

                elif event.value == 'RELEASE':
                    base_color = tuple(wm.coloraide_picker.mean)
                    # Direct brush color restore without sync
                    if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
                        ts.gpencil_paint.brush.color = base_color
                    if hasattr(ts, 'image_paint') and ts.image_paint.brush:
                        ts.image_paint.brush.color = base_color
                        if ts.unified_paint_settings.use_unified_color:
                            ts.unified_paint_settings.color = base_color

        return {'PASS_THROUGH'}

    def cleanup(self, context):
        """Reset state and colors"""
        wm = context.window_manager
        wm.coloraide_dynamics.running = False
        
        # Restore base color
        base_color = tuple(wm.coloraide_picker.mean)
        update_brush_color(context, base_color)

def register():
    bpy.utils.register_class(COLOR_OT_color_dynamics)

def unregister():
    bpy.utils.unregister_class(COLOR_OT_color_dynamics)