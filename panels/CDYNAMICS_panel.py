"""
Color dynamics panel - uses native Blender 5.0 Brush color jitter properties.
Compatible with Blender 4.4+ and 5.0+
UI matches Blender 5.0 native layout with collapsible style.
"""

import bpy
from ..COLORAIDE_mode_manager import ModeManager

def draw_dynamics_panel(layout, context):
    """
    Draw native Blender color jitter controls from the active brush.
    UI layout matches Blender 5.0's native "Randomize Color" panel
    with Coloraide's collapsible box style.
    
    All properties are on bpy.types.Brush:
    - use_color_jitter (bool) - Master toggle
    - hue_jitter, saturation_jitter, value_jitter (float 0-1) - Jitter amounts
    - use_stroke_random_hue/sat/val (bool) - Per-stroke toggles
    - use_random_press_hue/sat/val (bool) - Pressure sensitivity toggles
    - curve_random_hue/saturation/value (CurveMapping) - Pressure curves
    """
    wm = context.window_manager
    
    # Get current brush using ModeManager
    brush = ModeManager.get_current_brush(context)
    
    # Main collapsible box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_dynamics", 
        text="Color Dynamics", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_dynamics else 'TRIA_RIGHT',
        emboss=False
    )
    
    # Only draw contents if expanded
    if not wm.coloraide_display.show_dynamics:
        return
    
    # Check if brush exists
    if not brush:
        box.label(text="No active brush", icon='INFO')
        return
    
    # Check if brush has color jitter properties
    if not hasattr(brush, 'use_color_jitter'):
        box.label(text="Color jitter not available", icon='INFO')
        return
    
    # Master toggle for color jitter
    row = box.row()
    row.prop(brush, "use_color_jitter", text="Enable Randomization")
    
    # Main controls column - ALWAYS VISIBLE
    col = box.column(align=True)
    
    # Dim the controls if randomization is disabled (visual feedback only)
    col.enabled = brush.use_color_jitter
    
    # === HUE ROW ===
    row = col.row(align=True)
    row.prop(brush, "hue_jitter", text="Hue", slider=True)
    if hasattr(brush, 'use_stroke_random_hue'):
        row.prop(brush, "use_stroke_random_hue", text="", icon='GP_SELECT_STROKES', toggle=True)
    if hasattr(brush, 'use_random_press_hue'):
        row.prop(brush, "use_random_press_hue", text="", icon='STYLUS_PRESSURE', toggle=True)
    
    # Show pressure curve if enabled
    if hasattr(brush, 'use_random_press_hue') and brush.use_random_press_hue:
        if hasattr(brush, 'curve_random_hue'):
            col.template_curve_mapping(brush, "curve_random_hue", brush=True)
    
    # === SATURATION ROW ===
    row = col.row(align=True)
    row.prop(brush, "saturation_jitter", text="Saturation", slider=True)
    if hasattr(brush, 'use_stroke_random_sat'):
        row.prop(brush, "use_stroke_random_sat", text="", icon='GP_SELECT_STROKES', toggle=True)
    if hasattr(brush, 'use_random_press_sat'):
        row.prop(brush, "use_random_press_sat", text="", icon='STYLUS_PRESSURE', toggle=True)
    
    # Show pressure curve if enabled
    if hasattr(brush, 'use_random_press_sat') and brush.use_random_press_sat:
        if hasattr(brush, 'curve_random_saturation'):
            col.template_curve_mapping(brush, "curve_random_saturation", brush=True)
    
    # === VALUE ROW ===
    row = col.row(align=True)
    row.prop(brush, "value_jitter", text="Value", slider=True)
    if hasattr(brush, 'use_stroke_random_val'):
        row.prop(brush, "use_stroke_random_val", text="", icon='GP_SELECT_STROKES', toggle=True)
    if hasattr(brush, 'use_random_press_val'):
        row.prop(brush, "use_random_press_val", text="", icon='STYLUS_PRESSURE', toggle=True)
    
    # Show pressure curve if enabled
    if hasattr(brush, 'use_random_press_val') and brush.use_random_press_val:
        if hasattr(brush, 'curve_random_value'):
            col.template_curve_mapping(brush, "curve_random_value", brush=True)
