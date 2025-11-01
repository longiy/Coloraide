"""
Color dynamics properties for Blender 5.0+
Uses native brush jitter API instead of custom randomization system.
"""

import bpy
from bpy.props import FloatProperty, BoolProperty
from bpy.types import PropertyGroup

class ColoraideDynamicsProperties(PropertyGroup):
    """
    Properties for controlling native Blender color jitter.
    Maps a single "strength" value to Blender's hue/saturation/value jitter.
    """
    
    def update_dynamics_strength(self, context):
        """
        Update native jitter properties based on strength slider.
        This replaces the old modal operator approach.
        """
        # Get unified paint settings for current mode
        ts = context.tool_settings
        ups = None
        
        # Try to get mode-specific unified paint settings (Blender 5.0+)
        if context.mode == 'SCULPT' and hasattr(ts, 'sculpt'):
            ups = getattr(ts.sculpt, 'unified_paint_settings', None)
        elif context.mode == 'PAINT_TEXTURE' and hasattr(ts, 'image_paint'):
            ups = getattr(ts.image_paint, 'unified_paint_settings', None)
        elif context.mode == 'PAINT_VERTEX' and hasattr(ts, 'vertex_paint'):
            ups = getattr(ts.vertex_paint, 'unified_paint_settings', None)
        elif context.mode == 'PAINT_WEIGHT' and hasattr(ts, 'weight_paint'):
            ups = getattr(ts.weight_paint, 'unified_paint_settings', None)
        elif context.mode == 'PAINT_GPENCIL' and hasattr(ts, 'gpencil_paint'):
            ups = getattr(ts.gpencil_paint, 'unified_paint_settings', None)
        elif context.mode == 'VERTEX_GREASE_PENCIL' and hasattr(ts, 'gpencil_vertex_paint'):
            ups = getattr(ts.gpencil_vertex_paint, 'unified_paint_settings', None)
        
        if not ups:
            return
        
        # Convert strength (0-100) to jitter values (0.0-1.0)
        jitter = self.strength / 100.0
        
        # Set hue jitter (use full strength for hue variation)
        if hasattr(ups, 'hue_jitter'):
            ups.hue_jitter = jitter * self.hue_factor
        
        # Set saturation jitter (typically want less variation)
        if hasattr(ups, 'saturation_jitter'):
            ups.saturation_jitter = jitter * self.saturation_factor
        
        # Set value jitter if available (typically want less variation)
        if hasattr(ups, 'value_jitter'):
            ups.value_jitter = jitter * self.value_factor
    
    strength: FloatProperty(
        name="Color Dynamics",
        description="Overall amount of color randomization (uses native Blender jitter)",
        min=0.0,
        max=100.0,
        default=0.0,
        subtype='PERCENTAGE',
        update=update_dynamics_strength
    )
    
    # Factor controls for fine-tuning individual channels
    hue_factor: FloatProperty(
        name="Hue Factor",
        description="Multiplier for hue jitter (1.0 = full strength)",
        min=0.0,
        max=2.0,
        default=1.0
    )
    
    saturation_factor: FloatProperty(
        name="Saturation Factor", 
        description="Multiplier for saturation jitter (0.5 = half strength)",
        min=0.0,
        max=2.0,
        default=0.5
    )
    
    value_factor: FloatProperty(
        name="Value Factor",
        description="Multiplier for value jitter (0.5 = half strength)",
        min=0.0,
        max=2.0,
        default=0.5
    )
    
    show_advanced: BoolProperty(
        name="Show Advanced",
        description="Show individual HSV factor controls",
        default=False
    )


def register():
    pass


def unregister():
    pass
