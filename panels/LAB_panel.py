"""LAB slider panel UI implementation for Coloraide."""

import bpy

def draw_lab_panel(layout, context):
    wm = context.window_manager
    col = layout.column(align=True)
    
    # Lightness slider
    split = col.split(factor=0.15)
    split.label(text="L:")
    split.prop(wm.coloraide_lab, "lightness", text="", slider=True)
    
    # a slider
    split = col.split(factor=0.15)
    split.label(text="a:")
    split.prop(wm.coloraide_lab, "a", text="", slider=True)
    
    # b slider
    split = col.split(factor=0.15)
    split.label(text="b:")
    split.prop(wm.coloraide_lab, "b", text="", slider=True)