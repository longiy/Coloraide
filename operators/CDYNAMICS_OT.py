# CDYNAMICS_OT.py
import bpy
import random
from bpy.types import Operator
from ..COLORAIDE_sync import sync_all, is_updating
from ..COLORAIDE_brush_sync import update_brush_color

def apply_color_dynamics(master_color, strength):
    """Apply random color variation to a master color"""
    if strength <= 0:
        return master_color
    
    random_color = (random.random(), random.random(), random.random())
    strength_factor = strength / 100.0
    return tuple(
        master + (random - master) * strength_factor
        for master, random in zip(master_color, random_color)
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
    
    # Store state
    _active_stroke = False

    @classmethod
    def poll(cls, context):
        return context.window_manager.coloraide_dynamics.strength > 0

    def invoke(self, context, event):
        wm = context.window_manager
        wm.modal_handler_add(self)
        wm.coloraide_dynamics.running = True
        
        # Store current color as master color when starting
        if hasattr(wm, 'coloraide_picker'):
            current_color = tuple(wm.coloraide_picker.mean)
            wm.coloraide_dynamics.master_color = current_color
            
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        wm = context.window_manager
        
        if not wm.coloraide_dynamics.strength:
            self.cleanup(context)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            mouse_in_ui = is_mouse_in_ui(context, event)
            
            # Handle UI clicks normally
            if mouse_in_ui:
                return {'PASS_THROUGH'}
            
            # Only apply color dynamics for non-UI clicks
            if not mouse_in_ui:
                if event.value == 'PRESS':
                    # Start of a stroke - apply dynamics using master color
                    self._active_stroke = True
                    
                    # NEW: Always use master color for randomization
                    master_color = tuple(wm.coloraide_dynamics.master_color)
                    new_color = apply_color_dynamics(
                        master_color,
                        wm.coloraide_dynamics.strength
                    )
                    
                    # Update brush colors directly (not through sync_all to avoid updating Coloraide)
                    ts = context.tool_settings
                    
                    if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
                        ts.gpencil_paint.brush.color = new_color
                    
                    if hasattr(ts, 'gpencil_vertex_paint') and ts.gpencil_vertex_paint.brush:
                        ts.gpencil_vertex_paint.brush.color = new_color
                    
                    if hasattr(ts, 'image_paint') and ts.image_paint.brush:
                        ts.image_paint.brush.color = new_color
                        if ts.unified_paint_settings.use_unified_color:
                            ts.unified_paint_settings.color = new_color
                    
                    if hasattr(ts, 'vertex_paint') and ts.vertex_paint.brush:
                        ts.vertex_paint.brush.color = new_color

                elif event.value == 'RELEASE':
                    # End of a stroke - restore the master color
                    if self._active_stroke:
                        ts = context.tool_settings
                        master_color = tuple(wm.coloraide_dynamics.master_color)
                        
                        # Restore the master color to brushes
                        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
                            ts.gpencil_paint.brush.color = master_color
                        
                        if hasattr(ts, 'gpencil_vertex_paint') and ts.gpencil_vertex_paint.brush:
                            ts.gpencil_vertex_paint.brush.color = master_color
                        
                        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
                            ts.image_paint.brush.color = master_color
                            if ts.unified_paint_settings.use_unified_color:
                                ts.unified_paint_settings.color = master_color
                        
                        if hasattr(ts, 'vertex_paint') and ts.vertex_paint.brush:
                            ts.vertex_paint.brush.color = master_color
                    
                    # Reset stroke state
                    self._active_stroke = False

        return {'PASS_THROUGH'}

    def cleanup(self, context):
        """Reset state and colors"""
        wm = context.window_manager
        wm.coloraide_dynamics.running = False
        
        # Restore master color to brushes
        ts = context.tool_settings
        master_color = tuple(wm.coloraide_dynamics.master_color)
        
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = master_color
            
        if hasattr(ts, 'gpencil_vertex_paint') and ts.gpencil_vertex_paint.brush:
            ts.gpencil_vertex_paint.brush.color = master_color
            
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = master_color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = master_color
                
        if hasattr(ts, 'vertex_paint') and ts.vertex_paint.brush:
            ts.vertex_paint.brush.color = master_color