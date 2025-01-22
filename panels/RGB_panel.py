"""
RGB slider panel UI implementation for Coloraide.
"""

import bpy

def draw_rgb_panel(layout, context):
    """Draw RGB slider controls in the given layout"""
    wm = context.window_manager
    
    # RGB sliders box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_rgb_sliders", 
        text="RGB", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_rgb_sliders else 'TRIA_RIGHT', 
        emboss=False
    )
    
    if wm.coloraide_display.show_rgb_sliders:
        col = box.column(align=True)
        
        # Red slider
        split = col.split(factor=0.1)
        split.label(text="R:")
        row = split.row(align=True)
        row.prop(wm.coloraide_rgb, "red", text="", slider=True)
        row.operator(
            "color.sync_rgb",
            text="",
            icon='FILE_REFRESH'
        )
        
        # Green slider
        split = col.split(factor=0.1)
        split.label(text="G:")
        split.prop(wm.coloraide_rgb, "green", text="", slider=True)
        
        # Blue slider
        split = col.split(factor=0.1)
        split.label(text="B:")
        split.prop(wm.coloraide_rgb, "blue", text="", slider=True)

class RGB_PT_panel:
    """Class containing panel drawing methods for RGB controls"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the RGB controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_rgb_sliders:
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(wm.coloraide_rgb, "red", text="R")
            row.prop(wm.coloraide_rgb, "green", text="G")
            row.prop(wm.coloraide_rgb, "blue", text="B")
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full RGB control panel"""
        draw_rgb_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal RGB controls without labels"""
        wm = context.window_manager
        if wm.coloraide_display.show_rgb_sliders:
            col = layout.column(align=True)
            col.prop(wm.coloraide_rgb, "red", text="")
            col.prop(wm.coloraide_rgb, "green", text="")
            col.prop(wm.coloraide_rgb, "blue", text="")

def register():
    """Register any classes specific to the RGB panel"""
    pass

def unregister():
    """Unregister any classes specific to the RGB panel"""
    pass