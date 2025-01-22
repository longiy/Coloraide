"""
Property definitions for LAB color sliders.
"""

import bpy
from bpy.props import FloatProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_utils import (
    rgb_to_lab, lab_to_rgb,
    rgb_to_hsv, hsv_to_rgb,
    rgb_float_to_bytes, rgb_bytes_to_float
)


# Global state flags for update cycle prevention
_updating_lab = False
_updating_rgb = False
_updating_picker = False
_updating_hex = False
_updating_wheel = False

def is_lab_update_in_progress():
    """Check if any LAB color update cycle is in progress"""
    return any([
        _updating_lab,
        _updating_rgb,
        _updating_picker,
        _updating_hex,
        _updating_wheel
    ])

def sync_lab_from_rgb(context, rgb_color):
    """Sync LAB values from RGB color without triggering update cycles"""
    global _updating_lab
    _updating_lab = True
    try:
        lab_props = context.window_manager.coloraide_lab
        lab = rgb_to_lab(rgb_color)
        lab_props.lightness = lab[0]
        lab_props.a = lab[1]
        lab_props.b = lab[2]
    finally:
        _updating_lab = False

def update_lab(self, context):
    """Update handler for LAB slider changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    if _updating_rgb or _updating_picker or _updating_hex or _updating_wheel:
        return
    
    _updating_lab = True
    try:
        lab = (self.lightness, self.a, self.b)
        rgb = lab_to_rgb(lab)
        
        # Update picker values
        picker = context.window_manager.coloraide_picker
        picker.mean = rgb
        picker.current = rgb
        
        # Update wheel
        context.window_manager.coloraide_wheel.color = (*rgb, 1.0)
        
        # Update brush colors
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = rgb
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = rgb
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = rgb
                
    finally:
        _updating_lab = False

def validate_lightness(value):
    """Validate lightness value (0-100)"""
    return max(0.0, min(100.0, float(value)))

def validate_a(value):
    """Validate a value (-128 to 127)"""
    return max(-128.0, min(127.0, float(value)))

def validate_b(value):
    """Validate b value (-128 to 127)"""
    return max(-128.0, min(127.0, float(value)))

class ColoraideLABProperties(PropertyGroup):
    lightness: FloatProperty(
        name="L",
        description="Lightness (0-100)",
        default=50.0,
        min=0.0,
        max=100.0,
        precision=1,
        update=update_lab,
        set=validate_lightness
    )
    
    a: FloatProperty(
        name="a",
        description="Green (-) to Red (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=1,
        update=update_lab,
        set=validate_a
    )
    
    b: FloatProperty(
        name="b",
        description="Blue (-) to Yellow (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=1,
        update=update_lab,
        set=validate_b
    )

