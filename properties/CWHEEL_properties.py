"""
Standalone property definitions for color wheel handling.
"""

import bpy
from bpy.props import FloatProperty, FloatVectorProperty
from bpy.types import PropertyGroup

# Global state flags for update cycle prevention
_updating_wheel = False
_updating_rgb = False
_updating_picker = False
_updating_hex = False

def is_update_in_progress():
    """Check if any update cycle is in progress"""
    return any([
        _updating_wheel,
        _updating_rgb,
        _updating_picker,
        _updating_hex
    ])

def sync_wheel_from_color(context, color):
    """Sync wheel color from RGB without triggering updates"""
    global _updating_wheel
    _updating_wheel = True
    try:
        wheel_props = context.window_manager.coloraide_wheel
        wheel_props.color = (*color, 1.0)  # Add alpha channel
    finally:
        _updating_wheel = False

def update_from_wheel(self, context):
    """Update handler for color wheel changes"""
    global _updating_wheel, _updating_rgb, _updating_picker, _updating_hex
    
    if _updating_rgb or _updating_picker or _updating_hex:
        return
    
    _updating_wheel = True
    try:
        color = tuple(self.color[:3])  # Ignore alpha channel
        
        # Update picker values
        picker = context.window_manager.coloraide_picker
        picker.mean = color
        picker.current = color
        
        # Update hex
        if hasattr(context.window_manager, 'coloraide_hex'):
            context.window_manager.coloraide_hex.color = "#{:02X}{:02X}{:02X}".format(
                round(color[0] * 255),
                round(color[1] * 255),
                round(color[2] * 255)
            )
        
        # Update brush colors
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = color
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = color
                
    finally:
        _updating_wheel = False

class ColoraideWheelProperties(PropertyGroup):
    """Properties for color wheel"""
    
    def get_color(self):
        return self.get("color", (1.0, 1.0, 1.0, 1.0))
        
    def set_color(self, value):
        self["color"] = value
        
    scale: FloatProperty(
        name="Wheel Size",
        description="Adjust the size of the color wheel",
        min=1.0,
        max=3.0,
        default=1.5,
        step=10,
        precision=1
    )
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=update_from_wheel,
        get=get_color,
        set=set_color
    )
