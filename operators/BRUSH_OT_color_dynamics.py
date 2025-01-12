import bpy
import random
from bpy.app.handlers import persistent

# Store original colors and operator state
original_brush_color = {}

def apply_color_dynamics(color, dynamics_strength):
    """Apply color dynamics to an RGB color"""
    if dynamics_strength <= 0:
        return color
        
    # Generate random color
    random_color = (
        random.random(),
        random.random(),
        random.random()
    )
    
    # Lerp between original and random color based on dynamics strength
    return tuple(
        original + (random - original) * dynamics_strength
        for original, random in zip(color, random_color)
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
        return context.window_manager.color_dynamics_enable

    def invoke(self, context, event):
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
        wm = context.window_manager
        
        # Check if dynamics should be disabled
        if not wm.color_dynamics_enable:
            wm.color_dynamics_running = False
            self.restore_original_colors(context)
            self.cleanup(context)
            return {'CANCELLED'}

        if event.type == 'MOUSEMOVE':
            self._last_mouse = (event.mouse_x, event.mouse_y)

        # Detect stroke start/end
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self._stroke_active = True
                self._is_painting = True
            elif event.value == 'RELEASE':
                self._stroke_active = False
                self._is_painting = False
                self.restore_original_colors(context)

        # Update colors during stroke
        if self._stroke_active and self._is_painting:
            strength = wm.color_dynamics_strength / 100.0
            ts = context.tool_settings

            # Update Grease Pencil brush
            if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
                brush = ts.gpencil_paint.brush
                if 'gpencil' in original_brush_color:
                    new_color = apply_color_dynamics(original_brush_color['gpencil'], strength)
                    brush.color = new_color

            # Update Image Paint brush
            if hasattr(ts, 'image_paint') and ts.image_paint.brush:
                brush = ts.image_paint.brush
                if 'image_paint' in original_brush_color:
                    new_color = apply_color_dynamics(original_brush_color['image_paint'], strength)
                    brush.color = new_color
                    if ts.unified_paint_settings.use_unified_color and 'unified' in original_brush_color:
                        ts.unified_paint_settings.color = new_color

        return {'PASS_THROUGH'}

    def cleanup(self, context):
        """Clean up timer and restore colors"""
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        self.restore_original_colors(context)

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
        context.window_manager.color_dynamics_running = False
        self.cleanup(context)

def register():
    if not hasattr(bpy.types.WindowManager, "color_dynamics_running"):
        bpy.types.WindowManager.color_dynamics_running = bpy.props.BoolProperty(
            name="Color Dynamics Running",
            default=False
        )
    
    if not hasattr(bpy.types.WindowManager, "color_dynamics_strength"):
        bpy.types.WindowManager.color_dynamics_strength = bpy.props.IntProperty(
            name="Strength",
            description="Amount of random color variation during strokes",
            min=0,
            max=100,
            default=50,
            subtype='PERCENTAGE'
        )
    
    bpy.utils.register_class(BRUSH_OT_color_dynamics)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_color_dynamics)
    
    if hasattr(bpy.types.WindowManager, "color_dynamics_running"):
        del bpy.types.WindowManager.color_dynamics_running
    
    if hasattr(bpy.types.WindowManager, "color_dynamics_strength"):
        del bpy.types.WindowManager.color_dynamics_strength

def register():
    if not hasattr(bpy.types.WindowManager, "color_dynamics_running"):
        bpy.types.WindowManager.color_dynamics_running = bpy.props.BoolProperty(
            name="Color Dynamics Running",
            default=False
        )
    
    if not hasattr(bpy.types.WindowManager, "color_dynamics_strength"):
        bpy.types.WindowManager.color_dynamics_strength = bpy.props.IntProperty(
            name="Strength",
            description="Amount of random color variation during strokes",
            min=0,
            max=100,
            default=50,
            subtype='PERCENTAGE'
        )
    
    bpy.utils.register_class(BRUSH_OT_color_dynamics)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_color_dynamics)
    
    if hasattr(bpy.types.WindowManager, "color_dynamics_running"):
        del bpy.types.WindowManager.color_dynamics_running
    
    if hasattr(bpy.types.WindowManager, "color_dynamics_strength"):
        del bpy.types.WindowManager.color_dynamics_strength