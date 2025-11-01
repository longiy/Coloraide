"""
Color dynamics panel for Blender 5.0+
Now controls native Blender jitter instead of custom randomization.
"""

import bpy

def draw_dynamics_panel(layout, context):
    """
    Draw color dynamics controls using native Blender jitter.
    
    Args:
        layout: UI layout to draw into
        context: Blender context
    """
    wm = context.window_manager
    
    # Main strength slider
    row = layout.row(align=True)
    row.prop(wm.coloraide_dynamics, "strength", text="Color Dynamics", slider=True)
    
    # Optional: Show advanced controls
    if wm.coloraide_dynamics.strength > 0:
        col = layout.column(align=True)
        
        # Toggle for advanced controls
        row = col.row(align=True)
        row.prop(wm.coloraide_dynamics, "show_advanced", 
                text="Advanced", 
                icon='TRIA_DOWN' if wm.coloraide_dynamics.show_advanced else 'TRIA_RIGHT',
                emboss=False)
        
        if wm.coloraide_dynamics.show_advanced:
            box = col.box()
            box.label(text="HSV Jitter Factors:")
            
            split = box.split(factor=0.3)
            split.label(text="Hue:")
            split.prop(wm.coloraide_dynamics, "hue_factor", text="", slider=True)
            
            split = box.split(factor=0.3)
            split.label(text="Saturation:")
            split.prop(wm.coloraide_dynamics, "saturation_factor", text="", slider=True)
            
            split = box.split(factor=0.3)
            split.label(text="Value:")
            split.prop(wm.coloraide_dynamics, "value_factor", text="", slider=True)
            
            box.label(text="Native Blender jitter", icon='INFO')
