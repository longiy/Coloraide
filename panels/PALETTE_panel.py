"""
Palette panel UI implementation for Coloraide.
CLEANED: Removed unused PALETTE_PT_panel class with dead methods.
"""

import bpy
from .panel_helpers import draw_collapsible_header
from ..COLORAIDE_mode_manager import ModeManager

def draw_palette_panel(layout, context):
    """Draw palette controls in the given layout"""
    wm = context.window_manager
    box, is_open = draw_collapsible_header(layout, wm.coloraide_display, "show_palettes", "Color Palettes")

    if is_open:
        paint_settings = ModeManager.get_paint_settings(context)
            
        # Palette selector
        row = box.row(align=True)
        row.template_ID(paint_settings, "palette", new="palette.new")
        
        if paint_settings.palette:
            # Color selector UI
            add_row = box.row(align=True)
            palette_box = box.column()
            palette_box.template_palette(
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