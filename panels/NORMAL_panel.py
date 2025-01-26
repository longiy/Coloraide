
"""Normal color picker panel implementation."""

import bpy

def draw_normal_panel(layout, context):
    """Draw normal picker controls"""
    wm = context.window_manager
    
    # Normal picker box
    box = layout.box()
    row = box.row()
    
    # Toggle operator with dynamic icon
    op = row.operator("normal.color_picker", 
        text="Normal Color Sampler",
        icon='NORMALS_VERTEX' if wm.coloraide_normal.enabled else 'NORMALS_VERTEX_FACE',
        depress=wm.coloraide_normal.enabled
    )
    
    # Show space dropdown when enabled
    if wm.coloraide_normal.enabled:
        sub = box.row()
        sub.prop(wm.coloraide_normal, "space", text="Space")