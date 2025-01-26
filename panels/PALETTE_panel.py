"""Palette panel UI implementation for Coloraide."""
import bpy

def draw_palette_panel(layout, context):
    wm = context.window_manager
    box = layout.box()
    
    row = box.row()
    row.prop(wm.coloraide_display, "show_palettes", 
        text="Color Palettes", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_palettes else 'TRIA_RIGHT',
        emboss=False
    )
    
    if wm.coloraide_display.show_palettes:
        ts = context.tool_settings
        paint_settings = ts.gpencil_paint if context.mode == 'PAINT_GPENCIL' else ts.image_paint
        
        # Select/Create Palette  
        row = box.row(align=True)
        row.template_ID(paint_settings, "palette", new="palette.new")
        
        if paint_settings.palette:
            col = box.column()
            col.template_palette(paint_settings, "palette", color=True)
            
            # Add active color 
            row = box.row()
            op = row.operator(
                "palette.add_color",
                text="Add Current Color",
                icon='COLOR'
            )
            op.color = wm.coloraide_picker.mean