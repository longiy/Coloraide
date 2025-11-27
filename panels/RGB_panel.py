"""
RGB slider panel with color swatches before sliders.
"""

import bpy

def draw_rgb_panel(layout, context):
   """Draw RGB panel with color swatches before edge-to-edge sliders"""
   wm = context.window_manager
   
   col = layout.column(align=True)
   
   # RED CHANNEL
   row = col.row(align=True)
   split = row.split(factor=0.15, align=True)
   split.prop(wm.coloraide_rgb, "red_preview", text="")
   split.prop(wm.coloraide_rgb, 'red', text="", slider=True)
   
   # GREEN CHANNEL  
   row = col.row(align=True)
   split = row.split(factor=0.15, align=True)
   split.prop(wm.coloraide_rgb, "green_preview", text="")
   split.prop(wm.coloraide_rgb, 'green', text="", slider=True)
   
   # BLUE CHANNEL
   row = col.row(align=True)
   split = row.split(factor=0.15, align=True)
   split.prop(wm.coloraide_rgb, "blue_preview", text="")
   split.prop(wm.coloraide_rgb, 'blue', text="", slider=True)