import bpy
import random

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

class BRUSH_OT_color_dynamics(bpy.types.Operator):
    bl_idname = "brush.color_dynamics"
    bl_label = "Color Dynamics"
    bl_description = "Apply random color variation during brush strokes"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.color_dynamics.strength > 0

    def invoke(self, context, event):
        wm = context.window_manager
        wm.modal_handler_add(self)
        wm.color_dynamics.running = True
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        wm = context.window_manager
        
        if not wm.color_dynamics.strength:
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
                    ts = context.tool_settings
                    base_color = tuple(wm.coloraide_picker.mean)
                    
                    if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
                        ts.gpencil_paint.brush.color = apply_color_dynamics(
                            base_color,
                            wm.color_dynamics.strength
                        )

                    if hasattr(ts, 'image_paint') and ts.image_paint.brush:
                        new_color = apply_color_dynamics(
                            base_color,
                            wm.color_dynamics.strength
                        )
                        ts.image_paint.brush.color = new_color
                        if ts.unified_paint_settings.use_unified_color:
                            ts.unified_paint_settings.color = new_color

                elif event.value == 'RELEASE':
                    ts = context.tool_settings
                    base_color = tuple(wm.coloraide_picker.mean)
                    
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
        wm.color_dynamics.running = False
        
        ts = context.tool_settings
        base_color = tuple(wm.coloraide_picker.mean)
        
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = base_color
            
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = base_color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = base_color

def register():
    bpy.utils.register_class(BRUSH_OT_color_dynamics)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_color_dynamics)