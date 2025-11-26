"""
Object color properties panel UI implementation for Coloraide.
"""

import bpy


def draw_object_colors_panel(layout, context):
    """Draw object color properties panel"""
    wm = context.window_manager
    obj_colors = wm.coloraide_object_colors
    
    # Main collapsible box
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_object_colors",
        text="Object Colors",
        icon='TRIA_DOWN' if wm.coloraide_display.show_object_colors else 'TRIA_RIGHT',
        emboss=False
    )
    
    if not wm.coloraide_display.show_object_colors:
        return
    
    # Settings row
    settings_row = box.row(align=True)
    settings_row.operator("object_colors.refresh", text="Refresh", icon='FILE_REFRESH')
    settings_row.prop(obj_colors, "show_multiple_objects", text="Multi", toggle=True)
    
    # Check if we have any detected colors
    if not obj_colors.items:
        box.label(text="No colors detected", icon='INFO')
        box.label(text="Select object and click Refresh")
        return
    
    # Group colors by object name
    objects_dict = {}
    for idx, item in enumerate(obj_colors.items):
        obj_name = item.object_name
        if obj_name not in objects_dict:
            objects_dict[obj_name] = []
        objects_dict[obj_name].append((idx, item))
    
    # Draw each object's colors
    for obj_name, items in objects_dict.items():
        # Object header (collapsible)
        obj_box = box.box()
        obj_row = obj_box.row(align=True)
        
        # Store collapse state in window manager
        collapse_prop = f"obj_colors_collapse_{obj_name}"
        if not hasattr(wm, collapse_prop):
            wm[collapse_prop] = False
        
        is_collapsed = wm.get(collapse_prop, False)
        
        # Collapse toggle with object name
        icon = 'TRIA_DOWN' if not is_collapsed else 'TRIA_RIGHT'
        obj_row.prop(wm, f'["{collapse_prop}"]', 
                    text=obj_name, 
                    icon=icon, 
                    emboss=False,
                    toggle=True)
        
        # Show count
        obj_row.label(text=f"({len(items)})")
        
        # Only draw properties if not collapsed
        if not is_collapsed:
            # Column for all properties
            prop_col = obj_box.column(align=True)
            
            for idx, item in items:
                # Single row per property - regular spacing
                row = prop_col.row(align=True)
                row.scale_y = 1.0  # Regular vertical spacing
                
                # Live sync checkbox with fixed width
                sync_col = row.column(align=True)
                sync_col.scale_x = 0.8
                sync_col.prop(item, "live_sync", text="")
                
                # Small spacer to prevent text overlap
                row.separator(factor=0.5)
                
                # Split: left side (label) gets flexible space, right side (color+buttons) gets fixed space
                split = row.split(factor=0.65, align=True)
                
                # Left: Label - takes flexible space
                label_col = split.column(align=True)
                label_col.alignment = 'LEFT'
                label_col.label(text=item.label_short)
                
                # Right: Fixed-width section for color + buttons
                right_col = split.row(align=True)
                right_col.alignment = 'RIGHT'
                
                # Color swatch - fixed proportion of right section
                color_col = right_col.column(align=True)
                color_col.scale_x = 1.0
                color_col.prop(item, "color", text="")
                
                # Buttons - normal width, right next to color
                btn_row = right_col.row(align=True)
                btn_row.scale_x = 1.0
                
                # Pull button (↑) - Load color FROM object TO Coloraide (import)
                pull_op = btn_row.operator("object_colors.pull", text="", icon='TRIA_UP')
                pull_op.index = idx
                
                # Push button (↓) - Push color FROM Coloraide TO object (export)
                push_op = btn_row.operator("object_colors.push", text="", icon='TRIA_DOWN')
                push_op.index = idx
    
    # Summary at bottom
    total = len(obj_colors.items)
    synced = sum(1 for item in obj_colors.items if item.live_sync)
    if synced > 0:
        info_row = box.row(align=True)
        info_row.alignment = 'CENTER'
        info_row.label(text=f"{synced}/{total} live synced", icon='LINKED')