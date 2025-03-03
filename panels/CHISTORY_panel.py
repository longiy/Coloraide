"""
Color history panel UI implementation for Coloraide.
"""

import bpy
from ..COLORAIDE_brush_sync import update_brush_color, set_history_update_flag

def history_color_clicked(context, color):
    """Handle color history item clicks with priority"""
    # Set the flag to indicate this is a history update
    set_history_update_flag(True)
    try:
        # Update brush color with high priority
        update_brush_color(context, color, from_history=True)
        
        # Add to history as newest item (moves it to front)
        context.window_manager.coloraide_history.add_color(color)
    finally:
        # Always reset the flag when done
        set_history_update_flag(False)

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
        main_col = box.column(align=True)
        
        # Size adjustment row
        size_row = main_col.row(align=True)
        minus = size_row.operator("color.adjust_history_size", text="-")
        minus.increase = False
        plus = size_row.operator("color.adjust_history_size", text="+")
        plus.increase = True
        
        # Clear history button
        size_row.operator("color.clear_history", text="", icon='X')

        # Color swatches
        colors_per_row = 8
        history = list(wm.coloraide_history.items)
        
        # Only show swatches up to current history_size
        visible_history = history[:wm.coloraide_history.size]
        num_rows = (len(visible_history) + colors_per_row - 1) // colors_per_row
        
        for row_idx in range(num_rows):
            history_row = main_col.row(align=True)
            
            start_idx = row_idx * colors_per_row
            end_idx = min(start_idx + colors_per_row, len(visible_history))
            
            row_colors = visible_history[start_idx:end_idx]
            for item in row_colors:
                sub = history_row.row(align=True)
                # Use special operator for history color clicks
                op = sub.operator("color.use_history_color", text="")
                op.color = item.color
                sub.prop(item, "color", text="", icon_only=True)
            
            # Fill empty spots in last row
            empty_spots = colors_per_row - len(row_colors)
            if empty_spots > 0:
                for _ in range(empty_spots):
                    sub = history_row.row(align=True)
                    sub.enabled = False
                    sub.label(text="")