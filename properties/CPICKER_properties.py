"""
Core property definitions for color picker functionality.
"""

import bpy
from bpy.props import IntProperty, FloatVectorProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_utils import UpdateFlags

def sync_picker_from_brush(context, brush_color=None):
    """
    Synchronize picker colors from the current brush color.
    If brush_color is provided, use that instead of reading from the brush.
    """
    with UpdateFlags('picker'):
        wm = context.window_manager
        if not hasattr(wm, 'coloraide_picker'):
            return
            
        # If no color provided, get from brush
        if brush_color is None:
            ts = context.tool_settings
            if context.mode == 'PAINT_GPENCIL' and ts.gpencil_paint.brush:
                brush_color = tuple(ts.gpencil_paint.brush.color)
            elif hasattr(ts, 'image_paint') and ts.image_paint.brush:
                brush_color = tuple(ts.image_paint.brush.color)
                if ts.unified_paint_settings.use_unified_color:
                    brush_color = tuple(ts.unified_paint_settings.color)
        
        # Update picker colors
        if brush_color:
            wm.coloraide_picker.mean = brush_color
            wm.coloraide_picker.current = brush_color

# Rest of the ColoraidePickerProperties class definition remains the same
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
    
    mean: FloatVectorProperty(
        name="Mean Color",
        description="The mean RGB values of the picked pixels",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(0.5, 0.5, 0.5)
    )
    
    current: FloatVectorProperty(
        name="Current Color",
        description="The current RGB values under the cursor",
        size=3,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
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