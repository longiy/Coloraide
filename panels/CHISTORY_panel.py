"""
Color history panel UI implementation for Coloraide.
"""

import bpy

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
                sub.prop(item, "color", text="", event=True)
            
            # Fill empty spots in last row
            empty_spots = colors_per_row - len(row_colors)
            if empty_spots > 0:
                for _ in range(empty_spots):
                    sub = history_row.row(align=True)
                    sub.enabled = False
                    sub.label(text="")