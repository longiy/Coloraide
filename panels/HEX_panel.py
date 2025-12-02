"""
Hex color input panel UI implementation for Coloraide.
CLEANED: Removed unused HEX_PT_panel class with dead methods.
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