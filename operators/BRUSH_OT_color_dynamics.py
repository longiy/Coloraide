import bpy
import random

def apply_color_dynamics(original_color, strength):
    """Apply random color variation to a brush color"""
    if strength <= 0:
        return original_color
        
    # Generate new random color
    random_color = (random.random(), random.random(), random.random())
    
    # Blend between original and random color based on strength
    strength_factor = strength / 100.0
    return tuple(
        original + (random - original) * strength_factor
        for original, random in zip(original_color, random_color)
    )

class BRUSH_OT_color_dynamics(bpy.types.Operator):
    bl_idname = "brush.color_dynamics"
    bl_label = "Color Dynamics"
    bl_description = "Apply random color variation during brush strokes"
    bl_options = {'REGISTER'}

    original_colors = {}  # Store original brush colors

    @classmethod
    def poll(cls, context):
        return context.window_manager.color_dynamics_strength > 0

    def invoke(self, context, event):
        # Store original colors
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            self.original_colors['gpencil'] = ts.gpencil_paint.brush.color[:3]
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            self.original_colors['image_paint'] = ts.image_paint.brush.color[:3]
            if ts.unified_paint_settings.use_unified_color:
                self.original_colors['unified'] = ts.unified_paint_settings.color[:3]

        context.window_manager.modal_handler_add(self)
        context.window_manager.color_dynamics_running = True
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.window_manager.color_dynamics_strength <= 0:
            self.restore_colors(context)
            context.window_manager.color_dynamics_running = False
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                # Apply new random colors at stroke start
                strength = context.window_manager.color_dynamics_strength
                ts = context.tool_settings

                # Update Grease Pencil brush
                if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
                    if 'gpencil' in self.original_colors:
                        ts.gpencil_paint.brush.color = apply_color_dynamics(
                            self.original_colors['gpencil'], 
                            strength
                        )

                # Update Image Paint brush
                if hasattr(ts, 'image_paint') and ts.image_paint.brush:
                    if 'image_paint' in self.original_colors:
                        new_color = apply_color_dynamics(
                            self.original_colors['image_paint'], 
                            strength
                        )
                        ts.image_paint.brush.color = new_color
                        if ts.unified_paint_settings.use_unified_color:
                            ts.unified_paint_settings.color = new_color
                            
            elif event.value == 'RELEASE':
                self.restore_colors(context)

        return {'PASS_THROUGH'}

    def restore_colors(self, context):
        """Restore original brush colors"""
        ts = context.tool_settings
        
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            if 'gpencil' in self.original_colors:
                ts.gpencil_paint.brush.color = self.original_colors['gpencil']
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            if 'image_paint' in self.original_colors:
                ts.image_paint.brush.color = self.original_colors['image_paint']
                if ts.unified_paint_settings.use_unified_color:
                    ts.unified_paint_settings.color = self.original_colors['unified']

def register():
    bpy.utils.register_class(BRUSH_OT_color_dynamics)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_color_dynamics)