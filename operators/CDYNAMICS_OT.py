"""
Color dynamics operator for Blender 5.0+
NOTE: This operator is deprecated - native Blender jitter handles color randomization.
      The properties in CDYNAMICS_properties now directly control unified_paint_settings.
      
This file is kept for backward compatibility but the modal operator is removed.
"""

import bpy
from bpy.types import Operator

class COLOR_OT_color_dynamics(Operator):
    """
    Deprecated: Color dynamics now uses native Blender jitter.
    This operator exists for compatibility but does nothing.
    """
    bl_idname = "color.color_dynamics"
    bl_label = "Color Dynamics (Deprecated)"
    bl_description = "Color dynamics now uses native Blender jitter - this operator does nothing"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        self.report({'INFO'}, "Color dynamics now uses native Blender jitter API")
        return {'FINISHED'}


# Note: The old modal operator that manually randomized colors has been removed.
# Color randomization is now handled by Blender's native unified_paint_settings:
# - hue_jitter
# - saturation_jitter  
# - value_jitter (if available)
#
# These are controlled by the strength slider in CDYNAMICS_properties, which
# automatically updates the native jitter values when changed.
