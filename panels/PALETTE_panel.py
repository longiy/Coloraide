"""
Palette panel UI implementation for Coloraide.
"""

import bpy

def draw_palette_panel(layout, context):
    """Draw palette controls in the given layout"""
    wm = context.window_manager
    
    # Palette box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_palettes", 
        text="Color Palettes", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_palettes else 'TRIA_RIGHT',
        emboss=False
    )
    
    if wm.coloraide_display.show_palettes:
        ts = context.tool_settings
        
        # Get appropriate paint settings
        if context.mode == 'PAINT_GPENCIL':
            paint_settings = ts.gpencil_paint
        else:
            paint_settings = ts.image_paint
            
        # Palette selector and new button
        row = box.row(align=True)
        row.template_ID(paint_settings, "palette", new="palette.new")
        
        if paint_settings.palette:
            # Add current color button
            add_row = box.row(align=True)
            op = add_row.operator(
                "palette.add_color",
                text="Add Current",
                icon='ADD'
            )
            op.color = tuple(wm.coloraide_picker.mean)
            
            # Palette colors
            palette_box = box.column()
            palette_box.template_palette(
                paint_settings,
                "palette",
                color=True
            )
            
            # Remove color button (only show if a color is selected)
            if paint_settings.palette.colors.active:
                remove_row = box.row()
                remove_row.operator(
                    "palette.remove_color",
                    text="Remove Selected",
                    icon='REMOVE'
                )

class PALETTE_PT_panel:
    """Class containing panel drawing methods for palettes"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the palette controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_palettes:
            ts = context.tool_settings
            if context.mode == 'PAINT_GPENCIL':
                paint_settings = ts.gpencil_paint
            else:
                paint_settings = ts.image_paint
                
            row = layout.row(align=True)
            row.template_ID(paint_settings, "palette", new="palette.new")
            
            if paint_settings.palette:
                row.operator(
                    "palette.add_color",
                    text="",
                    icon='ADD'
                ).color = tuple(wm.coloraide_picker.mean)
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full palette panel"""
        draw_palette_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal palette controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_palettes:
            ts = context.tool_settings
            if context.mode == 'PAINT_GPENCIL':
                paint_settings = ts.gpencil_paint
            else:
                paint_settings = ts.image_paint
                
            if paint_settings.palette:
                layout.template_palette(
                    paint_settings,
                    "palette",
                    color=True
                )

def register():
    """Register any classes specific to the palette panel"""
    pass

def unregister():
    """Unregister any classes specific to the palette panel"""
    pass