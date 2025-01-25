"""
RGB slider panel UI implementation for Coloraide.
"""

import bpy

def draw_rgb_panel(layout, context):
    wm = context.window_manager
    
    # Remove the box wrapper and header
    col = layout.column(align=True)
    for channel, label in zip(['red', 'green', 'blue'], ['R:', 'G:', 'B:']):
        split = col.split(factor=0.15)
        split.label(text=label)
        split.prop(wm.coloraide_rgb, channel, text="", slider=True)