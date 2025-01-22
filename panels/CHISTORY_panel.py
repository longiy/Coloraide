"""
Color history panel UI implementation for Coloraide.
"""

import bpy
from ..operators.CHISTORY_OT import COLOR_OT_adjust_history_size

def draw_history_panel(layout, context):
    """Draw color history controls in the given layout"""
    wm = context.window_manager
    
    # History box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_history", 
        text=f"Color History ({wm.coloraide_history.size})", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_history else 'TRIA_RIGHT',
        emboss=False
    )
    
    if wm.coloraide_display.show_history:
        # Size adjustment row
        size_row = box.row(align=True)
        minus = size_row.operator("color.adjust_history_size", text="-")
        minus.increase = False
        plus = size_row.operator("color.adjust_history_size", text="+")
        plus.increase = True
        
        # Clear history button
        size_row.operator("color.clear_history", text="", icon='X')
        
        # Color swatches
        colors_per_row = 8
        history = list(wm.coloraide_history.items)
        
        # Only show swatches up to current history size
        visible_history = history[:wm.coloraide_history.size]
        num_rows = (len(visible_history) + colors_per_row - 1) // colors_per_row
        
        # Create column for swatch rows
        col = box.column(align=True)
        
        for row_idx in range(num_rows):
            history_row = col.row(align=True)
            
            start_idx = row_idx * colors_per_row
            end_idx = min(start_idx + colors_per_row, len(visible_history))
            
            row_colors = visible_history[start_idx:end_idx]
            for i, item in enumerate(row_colors):
                sub = history_row.row(align=True)
                sub.prop(item, "color", text="", event=True)
                
                # Add X button for individual color removal
                op = sub.operator(
                    "color.remove_history_color",
                    text="",
                    icon='X',
                    emboss=False
                )
                op.index = start_idx + i
            
            # Fill empty spots in the last row
            empty_spots = colors_per_row - len(row_colors)
            if empty_spots > 0:
                for _ in range(empty_spots):
                    sub = history_row.row(align=True)
                    sub.enabled = False
                    sub.label(text="")

class HISTORY_PT_panel:
    """Class containing panel drawing methods for color history"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the color history"""
        wm = context.window_manager
        if wm.coloraide_display.show_history:
            row = layout.row(align=True)
            for item in wm.coloraide_history.items[:8]:  # Show only first 8 colors
                row.prop(item, "color", text="")
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full color history panel"""
        draw_history_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal color history"""
        wm = context.window_manager
        if wm.coloraide_display.show_history:
            grid = layout.grid_flow(row_major=True, columns=8, align=True)
            for item in wm.coloraide_history.items[:wm.coloraide_history.size]:
                grid.prop(item, "color", text="")

def register():
    """Register any classes specific to the history panel"""
    pass

def unregister():
    """Unregister any classes specific to the history panel"""
    pass