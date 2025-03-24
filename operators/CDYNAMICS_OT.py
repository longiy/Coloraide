# CDYNAMICS_OT.py - Clean implementation
import bpy
import random
from bpy.types import Operator
from ..COLORAIDE_sync import is_updating

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

def update_brush_colors_directly(context, color):
    """Update only brush colors without affecting Coloraide storage"""
    ts = context.tool_settings
    
    # Store whether color monitor is running
    wm = context.window_manager
    monitor_running = False
    for op in wm.operators:
        if op.bl_idname == "color.monitor":
            monitor_running = True
            # Temporarily pause the monitor
            COLOR_OT_monitor.is_running = False
    
    try:
        # Update unified settings first if enabled
        if ts.unified_paint_settings.use_unified_color:
            ts.unified_paint_settings.color = color
                
        # Update individual brush colors if not using unified or if using both
        # Grease Pencil brush
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = color
            
        # Image Paint brush
        if hasattr(ts, 'image_paint') and ts.image_paint and ts.image_paint.brush:
            ts.image_paint.brush.color = color
            
        # Vertex Paint brush
        if hasattr(ts, 'vertex_paint') and ts.vertex_paint and ts.vertex_paint.brush:
            ts.vertex_paint.brush.color = color
    finally:
        # Resume monitor if it was running
        if monitor_running:
            COLOR_OT_monitor.is_running = True

class COLOR_OT_color_dynamics(Operator):
    bl_idname = "color.color_dynamics"
    bl_label = "Color Dynamics"
    bl_description = "Apply random color variation during brush strokes"
    bl_options = {'REGISTER'}
    
    # Store original picker color
    original_mean_color = None
    
    @classmethod
    def poll(cls, context):
        if not context.window_manager.coloraide_dynamics.strength:
            return False
            
        # Check if we're in a valid paint mode
        return context.mode in {'PAINT_GPENCIL', 'PAINT_TEXTURE', 'PAINT_VERTEX'}

    def invoke(self, context, event):
        wm = context.window_manager
        
        # Store original color
        self.original_mean_color = tuple(wm.coloraide_picker.mean)
        wm.coloraide_dynamics.base_color = self.original_mean_color
        
        # Mark that dynamics is running - used by monitor
        wm.coloraide_dynamics.running = True
        
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        wm = context.window_manager
        
        # Early exit if dynamics disabled
        if not wm.coloraide_dynamics.strength:
            self.cleanup(context)
            return {'CANCELLED'}
        
        # Check if the base color was updated by the monitor (from palette)
        if tuple(wm.coloraide_dynamics.base_color) != self.original_mean_color:
            # Update our stored reference to match
            self.original_mean_color = tuple(wm.coloraide_dynamics.base_color)

        if event.type == 'LEFTMOUSE':
            # Check for UI interaction
            if is_mouse_in_ui(context, event):
                return {'PASS_THROUGH'}
            
            if event.value == 'PRESS':
                # Check if user changed the base color (via wheel or sliders)
                current_mean = tuple(wm.coloraide_picker.mean)
                if current_mean != self.original_mean_color:
                    # Update our stored color to match
                    self.original_mean_color = current_mean
                    wm.coloraide_dynamics.base_color = current_mean
                
                # Generate dynamic color variation
                dynamic_color = apply_color_dynamics(
                    self.original_mean_color,
                    wm.coloraide_dynamics.strength
                )
                
                # Update brush colors directly without triggering monitor or sync
                update_brush_colors_directly(context, dynamic_color)
                
            elif event.value == 'RELEASE':
                # Restore to current base color
                update_brush_colors_directly(context, self.original_mean_color)

        return {'PASS_THROUGH'}

    def cleanup(self, context):
        """Reset state and restore brush colors to original color"""
        wm = context.window_manager
        wm.coloraide_dynamics.running = False
        
        # Restore to original picker color
        if self.original_mean_color:
            update_brush_colors_directly(context, self.original_mean_color)
        else:
            # Fallback if original color not stored
            update_brush_colors_directly(context, tuple(wm.coloraide_picker.mean))

# Modified monitor class reference (just enough for interaction with dynamics)
# The full implementation is in COLORAIDE_monitor.py
class COLOR_OT_monitor:
    is_running = False