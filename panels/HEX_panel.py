"""
Hex color input panel UI implementation for Coloraide.
"""

import bpy
from bpy.types import Operator

class COLOR_OT_validate_hex(Operator):
    """Validate and format hex color value"""
    bl_idname = "color.validate_hex"
    bl_label = "Validate Hex"
    bl_description = "Validate and format hex color value"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        hex_props = context.window_manager.coloraide_hex
        # Trigger validation through property setter
        hex_props.value = hex_props.value
        return {'FINISHED'}

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
        
        # Hex input field
        split = row.split(factor=0.8, align=True)
        hex_field = split.row(align=True)
        hex_field.prop(wm.coloraide_hex, "value", text="")
        
        # Add validation button
        buttons = split.row(align=True)
        buttons.operator(
            "color.validate_hex",
            text="",
            icon='CHECKMARK'
        )
        
        # Add help text
        help_row = box.row()
        help_row.label(text="Format: #RRGGBB (e.g. #FF0000 for red)")

def register():
    bpy.utils.register_class(COLOR_OT_validate_hex)

def unregister():
    bpy.utils.unregister_class(COLOR_OT_validate_hex)