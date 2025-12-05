"""
Object color properties panel UI with MODE TOGGLE and EXPLICIT RESCAN.
FIX: Added Rescan button, mode toggles no longer trigger refresh
"""

import bpy


def draw_object_mode(layout, context, obj_colors):
    """Draw Object Mode UI (individual property view)"""
    
    if not obj_colors.items:
        layout.label(text="No colors detected", icon='INFO')
        layout.label(text="Click 'Rescan' to detect colors")
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
        obj_box = layout.box()
        obj_row = obj_box.row(align=True)
        
        # Collapse state
        wm = context.window_manager
        collapse_prop = f"obj_colors_collapse_{obj_name}"
        if not hasattr(wm, collapse_prop):
            wm[collapse_prop] = False
        
        is_collapsed = wm.get(collapse_prop, False)
        icon = 'TRIA_DOWN' if not is_collapsed else 'TRIA_RIGHT'
        
        obj_row.prop(wm, f'["{collapse_prop}"]', 
                    text=obj_name, 
                    icon=icon, 
                    emboss=False,
                    toggle=True)
        obj_row.label(text=f"({len(items)})")
        
        # Draw properties if expanded
        if not is_collapsed:
            prop_col = obj_box.column(align=True)
            
            for idx, item in items:
                row = prop_col.row(align=True)
                row.scale_y = 1.0
                
                # Live sync checkbox
                sync_col = row.column(align=True)
                sync_col.scale_x = 0.8
                sync_col.prop(item, "live_sync", text="")
                
                row.separator(factor=0.5)
                
                # Split for label and color+buttons
                split = row.split(factor=0.65, align=True)
                
                # Label
                label_col = split.column(align=True)
                label_col.alignment = 'LEFT'
                label_col.label(text=item.label_short)
                
                # Color and buttons
                right_col = split.row(align=True)
                right_col.alignment = 'RIGHT'
                
                # Color swatch
                color_col = right_col.column(align=True)
                color_col.scale_x = 1.0
                color_col.prop(item, "color", text="")
                
                # Buttons
                btn_row = right_col.row(align=True)
                btn_row.scale_x = 1.0
                
                # Push (↑) - Load FROM object TO Coloraide
                push_op = btn_row.operator("object_colors.push", text="", icon='TRIA_UP')
                push_op.index = idx
                
                # Pull (↓) - Push FROM Coloraide TO object
                pull_op = btn_row.operator("object_colors.pull", text="", icon='TRIA_DOWN')
                pull_op.index = idx
    
    # Summary
    total = len(obj_colors.items)
    synced = sum(1 for item in obj_colors.items if item.live_sync)
    if synced > 0:
        info_row = layout.row(align=True)
        info_row.alignment = 'CENTER'
        info_row.label(text=f"{synced}/{total} live synced", icon='LINKED')


def draw_grouped_mode(layout, context, obj_colors):
    """Draw Grouped Mode UI (Figma-style color groups)"""
    
    if not obj_colors.items:
        layout.label(text="No colors detected", icon='INFO')
        layout.label(text="Click 'Rescan' to detect colors")
        return
    
    wm = context.window_manager
    
    for idx, item in enumerate(obj_colors.items):
        # Check if this is a grouped item
        if item.property_path != '__GROUP__':
            continue
        
        # Parse group data
        parts = item.object_name.split('|')
        count = int(parts[0])
        hex_val = parts[1]
        instances = parts[2:] if len(parts) > 2 else []
        
        display_label = item.label_short if item.label_short else f"{hex_val} ({count}×)"
        
        # Main row
        main_row = layout.row(align=True)
        main_row.scale_y = 1.0
        
        # Live sync checkbox
        sync_col = main_row.column(align=True)
        sync_col.scale_x = 0.8
        sync_col.prop(item, "live_sync", text="")
        
        main_row.separator(factor=0.5)
        
        # Split for label and color+buttons
        split = main_row.split(factor=0.65, align=True)
        
        # Build tooltip
        tooltip_lines = []
        for inst_str in instances:
            parts = inst_str.split(':')
            if len(parts) >= 2:
                obj_name = parts[0]
                prop_path = parts[1]
                
                if 'material' in prop_path.lower():
                    tooltip_lines.append(f"• {obj_name} > Material")
                elif 'light' in prop_path.lower() or 'data.color' in prop_path:
                    tooltip_lines.append(f"• {obj_name} > Light")
                elif 'modifiers' in prop_path:
                    tooltip_lines.append(f"• {obj_name} > GeoNodes")
                else:
                    tooltip_lines.append(f"• {obj_name} > Color")
        
        tooltip_text = "\n".join(tooltip_lines) if tooltip_lines else "No instances"
        
        # Label with tooltip
        label_col = split.column(align=True)
        label_col.alignment = 'LEFT'
        tooltip_op = label_col.operator("object_colors.show_tooltip", text=display_label, emboss=False)
        tooltip_op.tooltip = tooltip_text
        tooltip_op.label = display_label
        
        # Color and buttons
        right_col = split.row(align=True)
        right_col.alignment = 'RIGHT'
        
        # Color swatch
        color_col = right_col.column(align=True)
        color_col.scale_x = 1.0
        color_col.prop(item, "color", text="")
        
        # Buttons
        btn_row = right_col.row(align=True)
        btn_row.scale_x = 1.0
        
        # Push (↑) - Load FROM group TO Coloraide
        push_op = btn_row.operator("object_colors.push", text="", icon='TRIA_UP')
        push_op.index = idx
        
        # Pull (↓) - Push FROM Coloraide TO all in group
        pull_op = btn_row.operator("object_colors.pull", text="", icon='TRIA_DOWN')
        pull_op.index = idx
    
    # Summary
    total_groups = sum(1 for item in obj_colors.items if item.property_path == '__GROUP__')
    synced_groups = sum(1 for item in obj_colors.items 
                       if item.property_path == '__GROUP__' and item.live_sync)
    
    if synced_groups > 0:
        info_row = layout.row(align=True)
        info_row.alignment = 'CENTER'
        info_row.label(text=f"{synced_groups}/{total_groups} groups live synced", icon='LINKED')


def draw_object_colors_panel(layout, context):
    """Main panel drawing function with explicit Rescan button"""
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
    
    # CONTROL ROW: Multi toggle + Mode buttons + RESCAN
    control_row = box.row(align=True)
    
    # Multi toggle (left side)
    multi_col = control_row.column(align=True)
    multi_col.prop(obj_colors, "show_multiple_objects", text="Multi", icon='MOD_ARRAY', toggle=True)
    
    # Mode buttons (center)
    mode_row = control_row.row(align=True)
    mode_row.prop_enum(obj_colors, "display_mode", 'OBJECT', text="Object", icon='OBJECT_DATA')
    mode_row.prop_enum(obj_colors, "display_mode", 'GROUPED', text="Grouped", icon='COLOR')
    
    # RESCAN BUTTON (right side) - EXPLICIT ACTION
    rescan_col = control_row.column(align=True)
    rescan_col.operator("object_colors.refresh", text="Rescan", icon='FILE_REFRESH')
    
    # Draw mode-specific UI
    if obj_colors.display_mode == 'OBJECT':
        draw_object_mode(box, context, obj_colors)
    else:  # GROUPED
        draw_grouped_mode(box, context, obj_colors)