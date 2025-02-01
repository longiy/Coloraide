"""Normal color picker panel implementation."""
import bpy

def draw_normal_panel(layout, context):
    """Draw normal picker controls"""
    # Only show in 3D View and appropriate paint modes
    if context.area.type != 'VIEW_3D':
        return
    if context.mode not in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_WEIGHT'}:
        return
        
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