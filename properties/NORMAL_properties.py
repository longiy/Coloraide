"""Normal color picker property definitions."""
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatVectorProperty
from bpy.types import PropertyGroup

class ColoraideNormalProperties(PropertyGroup):
    enabled: BoolProperty(
        name="Normal Color Sampling",
        description="Sample normals as colors when painting",
        default=False
    )
    
    space: EnumProperty(
        name="Normal Space",
        description="Coordinate space for normal sampling",
        items=[
            ('OBJECT', "Object Space", "Use object space normals"),
            ('TANGENT', "Tangent Space", "Use tangent space normals (requires UV map)")
        ],
        default='OBJECT'
    )