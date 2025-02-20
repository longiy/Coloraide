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

def update_brush_colors(context, color, unified_only=False):
    """Update all brush colors efficiently"""
    ts = context.tool_settings
    
    # Update unified settings first if enabled
    if ts.unified_paint_settings.use_unified_color:
        ts.unified_paint_settings.color = color
        if unified_only:
            return
            
    # Update individual brush colors if not using unified
    if not ts.unified_paint_settings.use_unified_color:
        # Grease Pencil brush
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = color
            
        # Image Paint brush
        if hasattr(ts, 'image_paint') and ts.image_paint and ts.image_paint.brush:
            ts.image_paint.brush.color = color
            
        # Vertex Paint brush
        if hasattr(ts, 'vertex_paint') and ts.vertex_paint and ts.vertex_paint.brush:
            ts.vertex_paint.brush.color = color

class COLOR_OT_color_dynamics(Operator):
    bl_idname = "color.color_dynamics"
    bl_label = "Color Dynamics"
    bl_description = "Apply random color variation during brush strokes"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if not context.window_manager.coloraide_dynamics.strength:
            return False
            
        # Check if we're in a valid paint mode
        return context.mode in {'PAINT_GPENCIL', 'PAINT_TEXTURE', 'PAINT_VERTEX'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.coloraide_dynamics.base_color = tuple(wm.coloraide_picker.mean)
        wm.modal_handler_add(self)
        wm.coloraide_dynamics.running = True
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        wm = context.window_manager
        
        # Early exit if dynamics disabled
        if not wm.coloraide_dynamics.strength:
            self.cleanup(context)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            # Check for UI interaction
            if is_mouse_in_ui(context, event):
                return {'PASS_THROUGH'}
            
            if event.value == 'PRESS':
                # Generate dynamic color
                base_color = tuple(wm.coloraide_picker.mean)
                dynamic_color = apply_color_dynamics(
                    base_color,
                    wm.coloraide_dynamics.strength
                )
                
                # Update all brush colors efficiently
                update_brush_colors(context, dynamic_color)
                
            elif event.value == 'RELEASE':
                # Restore base color
                base_color = tuple(wm.coloraide_picker.mean)
                update_brush_colors(context, base_color)

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