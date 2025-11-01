"""
Color dynamics panel - uses native Blender 5.0 Brush color jitter properties.
Compatible with Blender 4.4+ and 5.0+
"""

import bpy
from ..COLORAIDE_mode_manager import ModeManager

def draw_dynamics_panel(layout, context):
    """
    Draw native Blender color jitter controls from the active brush.
    
    All properties are on bpy.types.Brush:
    - use_color_jitter (bool) - Master toggle
    - hue_jitter, saturation_jitter, value_jitter (float 0-1) - Jitter amounts
    - use_random_press_hue/sat/val (bool) - Pressure sensitivity toggles
    - curve_random_hue/saturation/value (CurveMapping) - Pressure curves
    - use_stroke_random_hue/sat/val (bool) - Per-stroke randomization
    """
    
    # Get current brush using ModeManager
    brush = ModeManager.get_current_brush(context)
    
    if not brush:
        layout.label(text="No active brush", icon='INFO')
        return
    
    # Check if brush has color jitter properties
    if not hasattr(brush, 'use_color_jitter'):
        layout.label(text="Color jitter not available for this brush", icon='INFO')
        return
    
    # Main box with collapsible header
    box = layout.box()
    row = box.row()
    
    # Master toggle
    row.prop(brush, "use_color_jitter", text="Randomize Color")
    
    # Only show controls if enabled
    if not brush.use_color_jitter:
        return
    
    # Jitter amount sliders
    col = box.column(align=True)
    
    # Hue jitter with pressure toggle
    row = col.row(align=True)
    sub = row.row(align=True)
    sub.prop(brush, "hue_jitter", text="Hue", slider=True)
    if hasattr(brush, 'use_random_press_hue'):
        sub.prop(brush, "use_random_press_hue", text="", icon='STYLUS_PRESSURE', toggle=True)
    
    # Show pressure curve if enabled
    if hasattr(brush, 'use_random_press_hue') and brush.use_random_press_hue:
        if hasattr(brush, 'curve_random_hue'):
            col.template_curve_mapping(brush, "curve_random_hue", brush=True)
    
    # Saturation jitter with pressure toggle
    row = col.row(align=True)
    sub = row.row(align=True)
    sub.prop(brush, "saturation_jitter", text="Saturation", slider=True)
    if hasattr(brush, 'use_random_press_sat'):
        sub.prop(brush, "use_random_press_sat", text="", icon='STYLUS_PRESSURE', toggle=True)
    
    # Show pressure curve if enabled
    if hasattr(brush, 'use_random_press_sat') and brush.use_random_press_sat:
        if hasattr(brush, 'curve_random_saturation'):
            col.template_curve_mapping(brush, "curve_random_saturation", brush=True)
    
    # Value jitter with pressure toggle
    row = col.row(align=True)
    sub = row.row(align=True)
    sub.prop(brush, "value_jitter", text="Value", slider=True)
    if hasattr(brush, 'use_random_press_val'):
        sub.prop(brush, "use_random_press_val", text="", icon='STYLUS_PRESSURE', toggle=True)
    
    # Show pressure curve if enabled
    if hasattr(brush, 'use_random_press_val') and brush.use_random_press_val:
        if hasattr(brush, 'curve_random_value'):
            col.template_curve_mapping(brush, "curve_random_value", brush=True)
    
    # Separator before stroke options
    col.separator()
    
    # Per-stroke randomization toggles (optional advanced feature)
    if (hasattr(brush, 'use_stroke_random_hue') or 
        hasattr(brush, 'use_stroke_random_sat') or 
        hasattr(brush, 'use_stroke_random_val')):
        
        col.label(text="Per-Stroke Randomization:")
        row = col.row(align=True)
        
        if hasattr(brush, 'use_stroke_random_hue'):
            row.prop(brush, "use_stroke_random_hue", text="Hue", toggle=True)
        if hasattr(brush, 'use_stroke_random_sat'):
            row.prop(brush, "use_stroke_random_sat", text="Sat", toggle=True)
        if hasattr(brush, 'use_stroke_random_val'):
            row.prop(brush, "use_stroke_random_val", text="Val", toggle=True)
    
    # Info label
    box.label(text="Native Blender color jitter", icon='INFO')