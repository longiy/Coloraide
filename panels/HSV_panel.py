"""
HSV slider panel UI implementation for Coloraide.
This module provides a self-contained UI drawing function for HSV controls.
"""

import bpy

def draw_hsv_panel(layout, context):
    """Draw HSV slider controls in the given layout"""
    wm = context.window_manager
    
    # HSV sliders box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_hsv_sliders", 
        text="HSV", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_hsv_sliders else 'TRIA_RIGHT', 
        emboss=False
    )
    
    if wm.coloraide_display.show_hsv_sliders:
        col = box.column(align=True)
        
        # Hue slider with color gradient background
        split = col.split(factor=0.1)
        split.label(text="H:")
        row = split.row(align=True)
        row.prop(wm.coloraide_hsv, "hue", text="", slider=True)
        
        # Add sync button to update HSV from current color
        row.operator(
            "color.sync_hsv",
            text="",
            icon='FILE_REFRESH'
        ).index = 0  # Using index in case we need to identify which slider triggered sync
        
        # Saturation slider
        split = col.split(factor=0.1)
        split.label(text="S:")
        split.prop(wm.coloraide_hsv, "saturation", text="", slider=True)
        
        # Value slider
        split = col.split(factor=0.1)
        split.label(text="V:")
        split.prop(wm.coloraide_hsv, "value", text="", slider=True)

class HSV_PT_panel:
    """Class containing panel drawing methods for HSV controls"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the HSV controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_hsv_sliders:
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(wm.coloraide_hsv, "hue", text="H")
            row.prop(wm.coloraide_hsv, "saturation", text="S")
            row.prop(wm.coloraide_hsv, "value", text="V")
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full HSV control panel"""
        draw_hsv_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal HSV controls without labels"""
        wm = context.window_manager
        if wm.coloraide_display.show_hsv_sliders:
            col = layout.column(align=True)
            col.prop(wm.coloraide_hsv, "hue", text="")
            col.prop(wm.coloraide_hsv, "saturation", text="")
            col.prop(wm.coloraide_hsv, "value", text="")

def register():
    """Register any classes specific to the HSV panel"""
    pass

def unregister():
    """Unregister any classes specific to the HSV panel"""
    pass