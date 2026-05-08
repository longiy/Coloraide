"""
Color wheel panel UI implementation for Coloraide.
Updated to remove color dynamics (now in separate panel).
"""

import bpy
from .panel_helpers import draw_collapsible_header

def draw_wheel_panel(layout, context):
    """Draw color wheel controls in the given layout"""
    wm = context.window_manager
    box, is_open = draw_collapsible_header(layout, wm.coloraide_display, "show_wheel", "Color Wheel")

    if is_open:
        # Color picker type dropdown (controls global Blender preference)
        prefs = context.preferences
        row = box.row(align=True)
        row.label(text="Color Picker Type")
        row.prop(prefs.view, "color_picker_type", text="")
        
        # Add the main color wheel with dynamic scaling
        col = box.column()
        col.scale_y = wm.coloraide_wheel.scale
        col.template_color_picker(
            wm.coloraide_wheel, 
            "color", 
            value_slider=True,
            lock_luminosity=False
        )
        
        # Create a single aligned column for all controls
        col = box.column(align=True)

        # Hex input, scale and reset
        row = col.row(align=True)
        split = row.split(factor=0.4, align=True)
        split.prop(wm.coloraide_hex, "value", text="")
        right_split = split.split(factor=0.85, align=True) 
        right_split.prop(wm.coloraide_wheel, "scale", text="Size", slider=True)
        right_split.operator(
            "color.reset_wheel_scale",
            text="",
            icon='LOOP_BACK'
        )

# Registration
def register():
    bpy.utils.register_class(COLOR_OT_reset_wheel_scale)

def unregister():
    bpy.utils.unregister_class(COLOR_OT_reset_wheel_scale)