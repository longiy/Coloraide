"""
Color wheel panel UI implementation for Coloraide.
Updated to remove color dynamics (now in separate panel).
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