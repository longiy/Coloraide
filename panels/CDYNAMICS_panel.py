# CDYNAMICS_panel.py
import bpy

def draw_dynamics_panel(layout, context):
    """Draw color dynamics controls in the given layout"""
    wm = context.window_manager

    row = layout.row(align=True)
    row.prop(wm.coloraide_dynamics, "strength", text="Strength", slider=True)