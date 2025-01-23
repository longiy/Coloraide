"""
Color wheel panel UI implementation for Coloraide.
"""

import bpy

def draw_wheel_panel(layout, context):
    """Draw color wheel controls in the given layout"""
    wm = context.window_manager
    
    # Color wheel box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_wheel", 
        text="Color Wheel", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_wheel else 'TRIA_RIGHT', 
        emboss=False
    )
    
    if wm.coloraide_display.show_wheel:
        # Add the main color wheel with dynamic scaling
        col = box.column()
        col.scale_y = wm.coloraide_wheel.scale
        col.template_color_picker(
            wm.coloraide_wheel, 
            "color", 
            value_slider=True,
            lock_luminosity=False
        )
        
        # Scale control with reset button
        row = box.row(align=True)
        split = row.split(factor=0.85, align=True)
        split.prop(wm.coloraide_wheel, "scale", text="Size", slider=True)
        split.operator(
            "color.reset_wheel_scale",
            text="",
            icon='LOOP_BACK'
        )

# Optional: Add operator for resetting wheel scale
class COLOR_OT_reset_wheel_scale(bpy.types.Operator):
    """Reset color wheel scale to default value"""
    bl_idname = "color.reset_wheel_scale"
    bl_label = "Reset Wheel Scale"
    bl_description = "Reset the color wheel size to default"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        context.window_manager.coloraide_wheel.scale = 1.5
        return {'FINISHED'}

# Registration
def register():
    bpy.utils.register_class(COLOR_OT_reset_wheel_scale)

def unregister():
    bpy.utils.unregister_class(COLOR_OT_reset_wheel_scale)