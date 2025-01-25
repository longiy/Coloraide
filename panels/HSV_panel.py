"""
HSV slider panel UI implementation for Coloraide.
"""

import bpy

def draw_hsv_panel(layout, context):
    """Draw HSV slider controls in the given layout"""
    wm = context.window_manager
    
    # # HSV sliders box with toggle
    # box = layout.box()
    # row = box.row()
    # row.prop(wm.coloraide_display, "show_hsv_sliders", 
    #     text="HSV", 
    #     icon='TRIA_DOWN' if wm.coloraide_display.show_hsv_sliders else 'TRIA_RIGHT',
    #     emboss=False
    # )
    
    # if wm.coloraide_display.show_hsv_sliders:
    col = box.column(align=True)
    
    # Hue slider with color gradient
    split = col.split(factor=0.15)
    split.label(text="H:")
    split.prop(wm.coloraide_hsv, "hue", text="", slider=True)
    
    # Saturation slider
    split = col.split(factor=0.15)
    split.label(text="S:")
    row = split.row(align=True)
    row.prop(wm.coloraide_hsv, "saturation", text="", slider=True)
    
    # Value slider
    split = col.split(factor=0.15)
    split.label(text="V:")
    row = split.row(align=True)
    row.prop(wm.coloraide_hsv, "value", text="", slider=True)
        
        # # Numerical display
        # row = box.row(align=True)
        # row.alignment = 'CENTER'
        # row.label(text=f"H: {wm.coloraide_hsv.hue:.1f}°, "
        #               f"S: {wm.coloraide_hsv.saturation:.1f}%, "
        #               f"V: {wm.coloraide_hsv.value:.1f}%")
        
        # # Description labels
        # col = box.column(align=True)
        # row = col.row(align=True)
        # row.alignment = 'CENTER'
        # row.label(text="H: Color Hue (0-360°)")
        # row = col.row(align=True)
        # row.alignment = 'CENTER'
        # row.label(text="S: Color Intensity (0-100%)")
        # row = col.row(align=True)
        # row.alignment = 'CENTER'
        # row.label(text="V: Brightness (0-100%)")

class HSV_PT_panel:
    """Class containing panel drawing methods for HSV controls"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the HSV controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_hsv_sliders:
            row = layout.row(align=True)
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