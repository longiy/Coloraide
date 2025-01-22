"""
Standalone property definitions for hex color handling.
"""

import bpy
from bpy.props import StringProperty
from bpy.types import PropertyGroup

# Global state flags for update cycle prevention
_updating_hex = False
_updating_rgb = False
_updating_picker = False
_updating_wheel = False

def is_hex_update_in_progress():
    """Check if any hex color update cycle is in progress"""
    return any([
        _updating_hex,
        _updating_rgb,
        _updating_picker,
        _updating_wheel
    ])

def validate_hex_value(value):
    """Validate and format hex color value"""
    value = value.strip().upper()
    if not value.startswith('#'):
        value = '#' + value
    
    # Remove invalid characters
    value = ''.join(c for c in value if c in '0123456789ABCDEF#')
    
    # Ensure proper length
    if len(value) > 7:
        value = value[:7]
    elif len(value) < 7:
        value = value.ljust(7, '0')
        
    return value

def sync_hex_from_rgb(context, color):
    """Sync hex value from RGB color without triggering updates"""
    global _updating_hex
    _updating_hex = True
    try:
        hex_props = context.window_manager.coloraide_hex
        hex_props.value = "#{:02X}{:02X}{:02X}".format(
            round(color[0] * 255),
            round(color[1] * 255),
            round(color[2] * 255)
        )
    finally:
        _updating_hex = False

def update_from_hex(self, context):
    """Update handler for hex color changes"""
    global _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    
    if _updating_rgb or _updating_picker or _updating_wheel:
        return
    
    if _updating_hex:
        return
        
    _updating_hex = True
    try:
        hex_str = self.value.lstrip('#')
        if len(hex_str) == 6:
            try:
                rgb_float = (
                    int(hex_str[0:2], 16) / 255.0,
                    int(hex_str[2:4], 16) / 255.0,
                    int(hex_str[4:6], 16) / 255.0
                )
                
                # Update picker values
                picker = context.window_manager.coloraide_picker
                picker.mean = rgb_float
                picker.current = rgb_float
                
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
                        
            except ValueError:
                pass
                
    finally:
        _updating_hex = False

class ColoraideHexProperties(PropertyGroup):
    """Properties for hex color handling"""
    
    value: StringProperty(
        name="Hex",
        description="Color in hex format (e.g. #FF0000)",
        default="#808080",
        maxlen=7,
        update=update_from_hex,
        set=validate_hex_value
    )