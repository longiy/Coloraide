"""
Property definitions for normal color sampling.
"""

import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import PropertyGroup

class ColoraideNormalProperties(PropertyGroup):
    """Properties for normal color sampling"""
    
    enabled: BoolProperty(
        name="Enable Normal Color Picking",
        description="Sample normals as colors when painting",
        default=False
    )
    
    space: EnumProperty(
        name="Normal Space",
        description="Coordinate space for normal sampling",
        items=[
            ('OBJECT', "Object Space", "Use object space normals"),
            ('TANGENT', "Tangent Space", "Use tangent space normals (requires UV map)"),
        ],
        default='OBJECT'
    )

