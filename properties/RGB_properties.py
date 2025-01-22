"""
Property definitions for RGB color sliders.
"""

import bpy
from bpy.props import IntProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_utils import (
    rgb_to_lab,
    lab_to_rgb,
    rgb_bytes_to_float,
    rgb_float_to_bytes
)

# Global state flags for update cycle prevention
_updating_rgb = False
_updating_picker = False
_updating_hex = False
_updating_wheel = False

def is_rgb_update_in_progress():
    """Check if any RGB color update cycle is in progress"""
    return any([
        _updating_rgb,
        _updating_picker,
        _updating_hex,
        _updating_wheel
    ])

def rgb_byte_to_float(rgb_byte):
    """Convert 0-255 RGB byte values to 0-1 float"""
    return tuple(c / 255 for c in rgb_byte)

def rgb_float_to_byte(rgb_float):
    """Convert 0-1 RGB float to 0-255 byte values"""
    return tuple(round(c * 255) for c in rgb_float)

def sync_rgb_from_brush(context, brush_color):
    """Sync RGB values from brush color without triggering update cycles"""
    global _updating_rgb
    _updating_rgb = True
    try:
        rgb_props = context.window_manager.coloraide_rgb
        rgb_bytes = rgb_float_to_byte(brush_color)
        rgb_props.red = rgb_bytes[0]
        rgb_props.green = rgb_bytes[1]
        rgb_props.blue = rgb_bytes[2]
    finally:
        _updating_rgb = False

def update_rgb_byte(self, context):
    """Update handler for RGB byte value changes"""
    global _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    if _updating_picker or _updating_hex or _updating_wheel:
        return
        
    _updating_rgb = True
    try:
        rgb_bytes = (self.red, self.green, self.blue)
        rgb_float = rgb_byte_to_float(rgb_bytes)
        
        # Update picker values
        picker = context.window_manager.coloraide_picker
        picker.mean = rgb_float
        picker.current = rgb_float
        
        # Update hex
        picker.hex_color = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        # Update wheel
        context.window_manager.coloraide_wheel.color = (*rgb_float, 1.0)
        
        # Update brush colors
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = rgb_float
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = rgb_float
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = rgb_float
                
    finally:
        _updating_rgb = False

def validate_rgb_value(value):
    """Validate RGB byte values (0-255)"""
    return max(0, min(255, int(value)))

class ColoraideRGBProperties(PropertyGroup):
    """Properties for RGB color sliders"""
    
    red: IntProperty(
        name="R",
        description="Red (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte,
        set=validate_rgb_value
    )
    
    green: IntProperty(
        name="G",
        description="Green (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte,
        set=validate_rgb_value
    )
    
    blue: IntProperty(
        name="B",
        description="Blue (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte,
        set=validate_rgb_value
        
    )

