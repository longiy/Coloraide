"""
Standalone property definitions for palette management.
"""

import bpy
from bpy.props import BoolProperty, FloatVectorProperty, StringProperty
from bpy.types import PropertyGroup
from ..operators.PALETTE_OT import (
    PALETTE_OT_add_color,
    PALETTE_OT_select_color,
    PALETTE_OT_remove_color
)

class ColoraidePaletteProperties(PropertyGroup):
    """Properties for palette management"""
    
    def get_active_paint_settings(self, context):
        """Get the active paint settings based on context"""
        ts = context.tool_settings
        if context.mode == 'PAINT_GPENCIL':
            return ts.gpencil_paint
        else:
            return ts.image_paint
    
    def get_current_palette(self, context):
        """Get the currently active palette"""
        paint_settings = self.get_active_paint_settings(context)
        return paint_settings.palette if paint_settings else None
    
    def update_preview_color(self, context):
        """Update the preview color when palette color is selected"""
        if self.suppress_updates:
            return
            
        color = self.preview_color
        wm = context.window_manager
        
        # Update picker color
        wm.coloraide_picker.mean = color
        wm.coloraide_picker.current = color
        
        # Update brush colors
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = color
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = color
    
    # Property to prevent update cycles
    suppress_updates: BoolProperty(
        default=False
    )
    
    # Preview color for selected palette entry
    preview_color: FloatVectorProperty(
        name="Preview Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_preview_color
    )
