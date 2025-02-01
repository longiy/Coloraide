"""Normal color picker property definitions."""
import bpy
from bpy.props import BoolProperty
from bpy.types import PropertyGroup

class ColoraideNormalProperties(PropertyGroup):
    enabled: BoolProperty(
        name="Normal Color Sampling",
        description="Sample normals as colors when painting, only work in 3D View",
        default=False
    )