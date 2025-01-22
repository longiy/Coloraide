"""
Property definitions for HSV color sliders.
"""

import bpy
from bpy.props import FloatProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_utils import (
    rgb_to_hsv,
    hsv_to_rgb,
    rgb_float_to_bytes,
    rgb_bytes_to_float
)

# Global state flags for update cycle prevention
_updating_hsv = False
_updating_rgb = False
_updating_picker = False
_updating_wheel = False

def is_hsv_update_in_progress():
    """Check if any HSV color update cycle is in progress"""
    return any([
        _updating_hsv,
        _updating_rgb,
        _updating_picker,
        _updating_wheel
    ])

def sync_hsv_from_rgb(context, rgb_color):
    """Sync HSV values from RGB color without triggering updates"""
    global _updating_hsv
    _updating_hsv = True
    try:
        hsv_props = context.window_manager.coloraide_hsv
        hsv = rgb_to_hsv(rgb_color)
        hsv_props.hue = hsv[0] * 360.0
        hsv_props.saturation = hsv[1] * 100.0
        hsv_props.value = hsv[2] * 100.0
    finally:
        _updating_hsv = False

def update_hsv(self, context):
    """Update handler for HSV slider changes"""
    global _updating_hsv, _updating_rgb, _updating_picker, _updating_wheel
    if _updating_rgb or _updating_picker or _updating_wheel:
        return
    
    _updating_hsv = True
    try:
        hsv = (
            self.hue / 360.0,
            self.saturation / 100.0,
            self.value / 100.0
        )
        rgb = hsv_to_rgb(hsv)
        
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
        _updating_hsv = False

def validate_hue(self, value):
    """Validate hue value to wrap around 360 degrees"""
    # Allow hue to wrap around
    return value % 360.0

def validate_saturation(self, value):
    """Validate saturation to stay within 0-100%"""
    return max(0.0, min(100.0, value))

def validate_value(self, value):
    """Validate value/brightness to stay within 0-100%"""
    return max(0.0, min(100.0, value))

class ColoraideHSVProperties(PropertyGroup):
    hue: FloatProperty(
        name="H",
        description="Hue (0-360°)",
        default=0.0,
        min=0.0,
        max=360.0,
        precision=1,
        update=update_hsv,
        set=validate_hue
    )
    
    saturation: FloatProperty(
        name="S",
        description="Saturation (0-100%)",
        default=0.0,
        min=0.0,
        max=100.0,
        precision=1,
        update=update_hsv,
        set=validate_saturation
    )
    
    value: FloatProperty(
        name="V",
        description="Value (0-100%)",
        default=100.0,
        min=0.0,
        max=100.0,
        precision=1,
        update=update_hsv,
        set=validate_value
    )