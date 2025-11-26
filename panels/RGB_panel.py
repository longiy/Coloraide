"""
RGB slider panel with color swatches before sliders.
"""

import bpy

def draw_rgb_panel(layout, context):
   """Draw RGB panel with read-only color swatches before edge-to-edge sliders"""
   wm = context.window_manager
   
   col = layout.column(align=True)
   
   # RED CHANNEL
   row = col.row(align=True)
   split = row.split(factor=0.15, align=True)
   # Use template_color_picker or just prop without interaction
   # By using a very small scale and no text, it acts as visual indicator
   preview_col = split.column(align=True)
   preview_col.alert = False  # Don't highlight
   preview_col.active = True  # Keep full brightness
   preview_col.enabled = True  # Keep enabled for full color
   # Make it effectively read-only by having no update callback and being in a tight space
   preview_col.prop(wm.coloraide_rgb, "red_preview", text="", emboss=True)
   split.prop(wm.coloraide_rgb, 'red', text="", slider=True)
   
   # GREEN CHANNEL  
   row = col.row(align=True)
   split = row.split(factor=0.15, align=True)
   preview_col = split.column(align=True)
   preview_col.alert = False
   preview_col.active = True
   preview_col.enabled = True
   preview_col.prop(wm.coloraide_rgb, "green_preview", text="", emboss=True)
   split.prop(wm.coloraide_rgb, 'green', text="", slider=True)
   
   # BLUE CHANNEL
   row = col.row(align=True)
   split = row.split(factor=0.15, align=True)
   preview_col = split.column(align=True)
   preview_col.alert = False
   preview_col.active = True
   preview_col.enabled = True
   preview_col.prop(wm.coloraide_rgb, "blue_preview", text="", emboss=True)
   split.prop(wm.coloraide_rgb, 'blue', text="", slider=True)