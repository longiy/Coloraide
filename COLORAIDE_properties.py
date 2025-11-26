"""
Central display properties for Coloraide addon.
Controls visibility of all panels and features.
"""

import bpy
from bpy.props import BoolProperty
from bpy.types import PropertyGroup

class ColoraideDisplayProperties(PropertyGroup):
    """Controls visibility of all Coloraide panels and features"""
    
    # Core picker visibility
    show_picker: BoolProperty(
        name="Show Color Picker",
        description="Show core color picker controls",
        default=True
    )
    
    show_stats: BoolProperty(
        name="Show Color Statistics",
        description="Show color statistics in picker panel",
        default=False
    )
    
    # Color space visibility
    show_rgb_sliders: BoolProperty(
        name="Show RGB Controls",
        description="Show RGB color controls",
        default=False
    )
    
    show_lab_sliders: BoolProperty(
        name="Show LAB Controls",
        description="Show LAB color controls",
        default=False
    )
    
    show_hsv_sliders: BoolProperty(
        name="Show HSV Controls",
        description="Show HSV color controls",
        default=True
    )
    
    show_hex_input: BoolProperty(
        name="Show Hex Input",
        description="Show hex color input field",
        default=True
    )
    
    show_wheel: BoolProperty(
        name="Show Color Wheel",
        description="Show color wheel control",
        default=True
    )
    
    show_color_sliders: BoolProperty(
        name="Show Color Sliders",
        description="Show color space sliders",
        default=True
    )
    
    # Color dynamics visibility
    show_dynamics: BoolProperty(
        name="Show Color Dynamics",
        description="Show color dynamics (randomization) controls",
        default=True
    )
    
    # Feature visibility
    show_history: BoolProperty(
        name="Show Color History",
        description="Show color history panel",
        default=True
    )
    
    show_palettes: BoolProperty(
        name="Show Color Palettes",
        description="Show color palette controls",
        default=True
    )

    show_palettes: BoolProperty(
        name="Show Color Palettes",
        description="Show color palette controls",
        default=True
    )
    
    show_object_colors: BoolProperty(
        name="Show Object Colors",
        description="Show detected color properties from selected objects",
        default=True
    )