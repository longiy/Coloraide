"""
Property definitions for palette management.
"""

import bpy
from bpy.props import BoolProperty, FloatVectorProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating, UpdateFlags

class ColoraidePaletteProperties(PropertyGroup):
    """Properties for palette management"""
    
    def get_active_paint_settings(self, context):
        """Get the active paint settings based on context"""
        ts = context.tool_settings
        if context.mode == 'PAINT_GPENCIL':
            return ts.gpencil_paint
        return ts.image_paint
    
    def update_preview_color(self, context):
        """Update handler for when palette color is selected"""
        if is_updating('palette'):
            return
            
        sync_all(context, 'palette', self.preview_color)
    
    preview_color: FloatVectorProperty(
        name="Preview Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_preview_color
    )
    
    def add_color(self, context, color):
        """Add a color to the active palette"""
        paint_settings = self.get_active_paint_settings(context)
        if not paint_settings or not paint_settings.palette:
            return False
            
        # Check for duplicate color
        for existing in paint_settings.palette.colors:
            if (abs(existing.color[0] - color[0]) < 0.001 and
                abs(existing.color[1] - color[1]) < 0.001 and
                abs(existing.color[2] - color[2]) < 0.001):
                return False
        
        # Add new color
        with UpdateFlags('palette'):
            new_color = paint_settings.palette.colors.new()
            new_color.color = color
            new_color.weight = 1.0
            return True