"""Base classes for Coloraide property groups."""

import bpy
from bpy.props import BoolProperty
from bpy.types import PropertyGroup


class SuppressUpdatesMixin(PropertyGroup):
    """Adds the suppress_updates guard shared by all Coloraide property groups.

    Do NOT register this class — only register concrete subclasses.
    """
    suppress_updates: BoolProperty(default=False)
