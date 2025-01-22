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
        row = box.row(align=True)
        # Hex input field with validation button
        split = row.split(factor=0.8, align=True)
        hex_field = split.row(align=True)
        hex_field.prop(wm.coloraide_hex, "value", text="")
        
        # Add buttons for sync and validation
        buttons = split.row(align=True)
        buttons.operator(
            "color.validate_hex",
            text="",
            icon='CHECKMARK'
        )
        buttons.operator(
            "color.sync_hex",
            text="",
            icon='FILE_REFRESH'
        )
        
        # Add help text
        help_row = box.row()
        help_row.label(text="Format: #RRGGBB (e.g. #FF0000 for red)")

class HEX_PT_panel:
    """Class containing panel drawing methods for hex color input"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the hex input"""
        wm = context.window_manager
        if wm.coloraide_display.show_hex_input:
            row = layout.row(align=True)
            row.prop(wm.coloraide_hex, "value", text="")
            row.operator(
                "color.sync_hex",
                text="",
                icon='FILE_REFRESH'
            )
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full hex input panel"""
        draw_hex_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal hex input without labels"""
        wm = context.window_manager
        if wm.coloraide_display.show_hex_input:
            layout.prop(wm.coloraide_hex, "value", text="")

def register():
    """Register any classes specific to the hex panel"""
    pass

def unregister():
    """Unregister any classes specific to the hex panel"""
    pass