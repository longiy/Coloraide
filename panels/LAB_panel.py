"""
LAB slider panel UI implementation for Coloraide.
"""

import bpy

def draw_lab_panel(layout, context):
    """Draw LAB slider controls in the given layout"""
    wm = context.window_manager
    
    # LAB sliders box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_lab_sliders", 
        text="LAB", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_lab_sliders else 'TRIA_RIGHT',
        emboss=False
    )
    
    if wm.coloraide_display.show_lab_sliders:
        col = box.column(align=True)
        
        # Lightness slider
        split = col.split(factor=0.15)
        split.label(text="L:")
        split.prop(wm.coloraide_lab, "lightness", text="", slider=True)
        
        # a slider
        split = col.split(factor=0.15)
        split.label(text="a:")
        row = split.row(align=True)
        row.prop(wm.coloraide_lab, "a", text="", slider=True)
        
        # b slider
        split = col.split(factor=0.15)
        split.label(text="b:")
        row = split.row(align=True)
        row.prop(wm.coloraide_lab, "b", text="", slider=True)
        
        # Numerical display
        row = box.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=f"L: {wm.coloraide_lab.lightness:.1f}, "
                      f"a: {wm.coloraide_lab.a:.1f}, "
                      f"b: {wm.coloraide_lab.b:.1f}")
        
        # Description labels
        col = box.column(align=True)
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="L: Black (0) to White (100)")
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="a: Green (-) to Red (+)")
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="b: Blue (-) to Yellow (+)")

class LAB_PT_panel:
    """Class containing panel drawing methods for LAB controls"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the LAB controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_lab_sliders:
            row = layout.row(align=True)
            row.prop(wm.coloraide_lab, "lightness", text="L")
            row.prop(wm.coloraide_lab, "a", text="a")
            row.prop(wm.coloraide_lab, "b", text="b")
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full LAB control panel"""
        draw_lab_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal LAB controls without labels"""
        wm = context.window_manager
        if wm.coloraide_display.show_lab_sliders:
            col = layout.column(align=True)
            col.prop(wm.coloraide_lab, "lightness", text="")
            col.prop(wm.coloraide_lab, "a", text="")
            col.prop(wm.coloraide_lab, "b", text="")

def register():
    """Register any classes specific to the LAB panel"""
    pass

def unregister():
    """Unregister any classes specific to the LAB panel"""
    pass