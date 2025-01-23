"""
RGB slider panel UI implementation for Coloraide.
"""

import bpy

def draw_rgb_panel(layout, context):
    wm = context.window_manager
    
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_rgb_sliders", 
        text="RGB", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_rgb_sliders else 'TRIA_RIGHT',
        emboss=False
    )
    
    if wm.coloraide_display.show_rgb_sliders:
        col = box.column(align=True)
        
        # RGB sliders
        for channel, label in zip(['red', 'green', 'blue'], ['R:', 'G:', 'B:']):
            split = col.split(factor=0.15)
            split.label(text=label)
            split.prop(wm.coloraide_rgb, channel, text="", slider=True)
        
        # Alpha slider
        split = col.split(factor=0.15)
        split.label(text="A:")
        split.prop(wm.coloraide_rgb, "alpha", text="", slider=True)
        
        # Numeric display
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text=f"({wm.coloraide_rgb.red}, {wm.coloraide_rgb.green}, {wm.coloraide_rgb.blue})")


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
            row.prop(wm.coloraide_rgb, "alpha", text="A")
    
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
            col.prop(wm.coloraide_rgb, "alpha", text="")

def register():
    """Register any classes specific to the RGB panel"""
    pass

def unregister():
    """Unregister any classes specific to the RGB panel"""
    pass