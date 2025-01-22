"""
Core property definitions for color picker functionality.
"""

import bpy
from bpy.props import IntProperty, FloatVectorProperty
from bpy.types import PropertyGroup

# Global state flags for update cycle prevention
_updating_picker = False
_updating_rgb = False
_updating_lab = False
_updating_hsv = False
_updating_hex = False
_updating_wheel = False
_user_is_editing = False

def is_update_in_progress():
    """Check if any color update cycle is in progress"""
    return any([
        _updating_picker,
        _updating_rgb,
        _updating_lab,
        _updating_hsv,
        _updating_hex,
        _updating_wheel
    ])

def sync_picker_from_brush(context, brush_color):
    """Sync picker values from brush color without triggering updates"""
    global _updating_picker
    _updating_picker = True
    try:
        picker = context.window_manager.coloraide_picker
        picker.mean = brush_color
        picker.current = brush_color
        
        # Update statistical values
        picker.max = brush_color
        picker.min = brush_color
        picker.median = brush_color
        
        # Sync to other color spaces if they exist
        if hasattr(context.window_manager, 'coloraide_rgb'):
            rgb_bytes = tuple(round(c * 255) for c in brush_color)
            context.window_manager.coloraide_rgb.red = rgb_bytes[0]
            context.window_manager.coloraide_rgb.green = rgb_bytes[1]
            context.window_manager.coloraide_rgb.blue = rgb_bytes[2]
            
        if hasattr(context.window_manager, 'coloraide_hex'):
            context.window_manager.coloraide_hex.value = "#{:02X}{:02X}{:02X}".format(
                round(brush_color[0] * 255),
                round(brush_color[1] * 255),
                round(brush_color[2] * 255)
            )
            
        if hasattr(context.window_manager, 'coloraide_wheel'):
            context.window_manager.coloraide_wheel.color = (*brush_color, 1.0)
            
    finally:
        _updating_picker = False

def update_picker_color(self, context):
    """Update handler for picker color changes"""
    global _updating_picker, _updating_rgb, _updating_lab, _updating_hsv
    global _updating_hex, _updating_wheel
    
    if _updating_rgb or _updating_lab or _updating_hsv or _updating_hex or _updating_wheel:
        return
        
    _updating_picker = True
    try:
        # Clamp color values
        color = tuple(max(0, min(1, c)) for c in self.mean)
        
        # Update brush colors
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = color
            
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = color
                
        # Add to history if enabled
        if hasattr(context.window_manager, 'coloraide_history'):
            context.window_manager.coloraide_history.add_color(color)
            
    finally:
        _updating_picker = False

class ColoraidePickerProperties(PropertyGroup):
    """Properties for core color picker functionality"""
    
    custom_size: IntProperty(
        name="Quick Pick Size",
        description="Custom tile size for quick picker",
        default=10,
        min=1,
        soft_max=100,
        soft_min=5
    )
    
    def get_mean(self):
        return self.get("mean", (0.5, 0.5, 0.5))
        
    def set_mean(self, value):
        self["mean"] = value
        
    mean: FloatVectorProperty(
        name="Mean Color",
        description="The mean RGB values of the picked pixels",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(0.5, 0.5, 0.5),
        update=update_picker_color,
        get=get_mean,
        set=set_mean
    )
    
    def get_current(self):
        return self.get("current", (1.0, 1.0, 1.0))
        
    def set_current(self, value):
        self["current"] = value
    
    current: FloatVectorProperty(
        name="Current Color",
        description="The current RGB values under the cursor",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        get=get_current,
        set=set_current
    )
    
    max: FloatVectorProperty(
        name="Maximum",
        description="The maximum RGB values in the sample area",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
    )
    
    min: FloatVectorProperty(
        name="Minimum",
        description="The minimum RGB values in the sample area",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0)
    )
    
    median: FloatVectorProperty(
        name="Median",
        description="The median RGB values in the sample area",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(0.5, 0.5, 0.5)
    )

