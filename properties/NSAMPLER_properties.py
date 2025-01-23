"""
Property definitions for normal color sampling.
"""

import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating

class ColoraideNormalProperties(PropertyGroup):
    """Properties for normal color sampling"""
    
    def update_enabled(self, context):
        """Handle normal sampler enable/disable"""
        if self.enabled:
            # Start normal sampling operator when enabled
            if not any(op.bl_idname == "brush.sample_normal" 
                      for op in context.window_manager.operators):
                bpy.ops.brush.sample_normal('INVOKE_DEFAULT')
    
    enabled: BoolProperty(
        name="Enable Normal Color Picking",
        description="Sample normals as colors when painting",
        default=False,
        update=update_enabled
    )
    
    space: EnumProperty(
        name="Normal Space",
        description="Coordinate space for normal sampling",
        items=[
            ('OBJECT', "Object Space", "Use object space normals"),
            ('TANGENT', "Tangent Space", "Use tangent space normals (requires UV map)"),
            ('UV', "UV Space", "Use UV space normals (Image Editor only)")
        ],
        default='TANGENT'
    )