"""
Hex color input panel UI implementation for Coloraide.
"""

import bpy

def draw_hex_panel(layout, context):
    """Draw hex color input controls in the given layout"""
    wm = context.window_manager
    
    # Hex input box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_hex_input", 
        text="Hex Color", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_hex_input else 'TRIA_RIGHT', 
        emboss=False
    )
    
    if wm.coloraide_display.show_hex_input:
        # Hex input field
        row = box.row(align=True)
        row.prop(wm.coloraide_hex, "value", text="")
        
        # Add help text
        box.label(text="Format: #RRGGBB (e.g. #FF0000 for red)")

class HEX_PT_panel:
    """Class containing panel drawing methods for hex input"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the hex input"""
        wm = context.window_manager
        if wm.coloraide_display.show_hex_input:
            layout.prop(wm.coloraide_hex, "value", text="")
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full hex input panel"""
        draw_hex_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal hex input"""
        wm = context.window_manager
        if wm.coloraide_display.show_hex_input:
            layout.prop(wm.coloraide_hex, "value", text="")