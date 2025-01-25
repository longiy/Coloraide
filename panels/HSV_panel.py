"""HSV slider panel UI implementation for Coloraide."""

import bpy

def draw_hsv_panel(layout, context):
    wm = context.window_manager
    col = layout.column(align=True)
    
    # Hue slider
    split = col.split(factor=0.15)
    split.label(text="H:")
    split.prop(wm.coloraide_hsv, "hue", text="", slider=True)
    
    # Saturation slider
    split = col.split(factor=0.15)
    split.label(text="S:")
    split.prop(wm.coloraide_hsv, "saturation", text="", slider=True)
    
    # Value slider
    split = col.split(factor=0.15)
    split.label(text="V:")
    split.prop(wm.coloraide_hsv, "value", text="", slider=True)