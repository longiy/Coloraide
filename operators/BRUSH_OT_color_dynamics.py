import bpy
import random

# Store original colors and operator state
original_brush_color = {}
current_random_color = None

def apply_color_dynamics(color, dynamics_strength, force_new=False):
    """Apply color dynamics to an RGB color"""
    global current_random_color
    
    if dynamics_strength <= 0:
        return color
        
    # Generate new random color only if needed
    if current_random_color is None or force_new:
        current_random_color = (
            random.random(),
            random.random(),
            random.random()
        )
    
    # Lerp between original and random color based on dynamics strength
    strength_factor = dynamics_strength / 100.0
    return tuple(
        original + (random - original) * strength_factor
        for original, random in zip(color, current_random_color)
    )

class BRUSH_OT_color_dynamics(bpy.types.Operator):
    bl_idname = "brush.color_dynamics"
    bl_label = "Color Dynamics"
    bl_description = "Apply random color variation during brush strokes"
    bl_options = {'REGISTER'}

    _stroke_active = False
    _timer = None
    _last_mouse = None
    _is_painting = False

    @classmethod
    def poll(cls, context):
        # Always allow the operator when strength > 0
        return context.window_manager.color_dynamics_strength > 0

    def invoke(self, context, event):
        global current_random_color
        current_random_color = None
        
        self._stroke_active = False
        self._last_mouse = None
        self._is_painting = False
        
        # Store initial colors
        self.store_original_colors(context)
        
        # Add the timer for updates
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        
        context.window_manager.color_dynamics_running = True
        return {'RUNNING_MODAL'}

    def store_original_colors(self, context):
        """Store the original brush colors"""
        ts = context.tool_settings
        
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            brush = ts.gpencil_paint.brush
            original_brush_color['gpencil'] = brush.color[:3]
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            brush = ts.image_paint.brush
            original_brush_color['image_paint'] = brush.color[:3]
            if ts.unified_paint_settings.use_unified_color:
                original_brush_color['unified'] = ts.unified_paint_settings.color[:3]

    def modal(self, context, event):
        global current_random_color
        wm = context.window_manager
        
        # Check if we should still be running
        if wm.color_dynamics_strength <= 0:
            self.cleanup(context)
            return {'CANCELLED'}
            
        # Update stroke state
        if event.type == 'MOUSEMOVE':
            self._last_mouse = (event.mouse_x, event.mouse_y)

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                # Start new stroke - generate new random color
                self._stroke_active = True
                self._is_painting = True
                
                # Apply new random color
                strength = wm.color_dynamics_strength
                ts = context.tool_settings

                # Update Grease Pencil brush
                if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
                    brush = ts.gpencil_paint.brush
                    if 'gpencil' in original_brush_color:
                        new_color = apply_color_dynamics(original_brush_color['gpencil'], strength, True)
                        brush.color = new_color

                # Update Image Paint brush
                if hasattr(ts, 'image_paint') and ts.image_paint.brush:
                    brush = ts.image_paint.brush
                    if 'image_paint' in original_brush_color:
                        new_color = apply_color_dynamics(original_brush_color['image_paint'], strength, True)
                        brush.color = new_color
                        if ts.unified_paint_settings.use_unified_color and 'unified' in original_brush_color:
                            ts.unified_paint_settings.color = new_color
                            
            elif event.value == 'RELEASE':
                self._stroke_active = False
                self._is_painting = False
                self.restore_original_colors(context)
                # Generate new random color for next stroke
                current_random_color = None

        # Continue monitoring events
        return {'PASS_THROUGH'}

    def cleanup(self, context):
        """Clean up timer and restore colors"""
        global current_random_color
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        current_random_color = None
        self.restore_original_colors(context)
        context.window_manager.color_dynamics_running = False

    def restore_original_colors(self, context):
        """Restore the original brush colors"""
        ts = context.tool_settings
        
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            if 'gpencil' in original_brush_color:
                ts.gpencil_paint.brush.color = original_brush_color['gpencil']
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            if 'image_paint' in original_brush_color:
                ts.image_paint.brush.color = original_brush_color['image_paint']
            if ts.unified_paint_settings.use_unified_color and 'unified' in original_brush_color:
                ts.unified_paint_settings.color = original_brush_color['unified']

    def cancel(self, context):
        """Handle operator cancellation"""
        self.cleanup(context)

def register():
    bpy.utils.register_class(BRUSH_OT_color_dynamics)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_color_dynamics)