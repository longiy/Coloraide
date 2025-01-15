"""
Property group definitions for Coloraide addon with synchronization.
"""

import bpy
from bpy.props import (
    BoolProperty, 
    IntProperty, 
    FloatProperty, 
    FloatVectorProperty,
    StringProperty
)
from bpy.types import PropertyGroup
from .utils.color_conversions import rgb_to_lab, lab_to_rgb

# Global state flags for update cycle prevention
_updating_lab = False
_updating_rgb = False
_updating_picker = False
_updating_hex = False
_updating_wheel = False

def rgb_float_to_byte(rgb_float):
    """Convert 0-1 RGB float to 0-255 byte values"""
    return tuple(round(c * 255) for c in rgb_float)

def rgb_byte_to_float(rgb_byte):
    """Convert 0-255 RGB byte values to 0-1 float"""
    return tuple(c / 255 for c in rgb_byte)

def update_all_colors(color, context):
    """Update colors and store originals"""
    ts = context.tool_settings
    
    # Update brush colors
    if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
        ts.gpencil_paint.brush.color = color
    
    if hasattr(ts, 'image_paint') and ts.image_paint.brush:
        ts.image_paint.brush.color = color
        if ts.unified_paint_settings.use_unified_color:
            ts.unified_paint_settings.color = color

def update_from_wheel(self, context):
    """Update handler for color wheel changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    if _updating_lab or _updating_rgb or _updating_picker or _updating_hex:
        return
        
    _updating_wheel = True
    try:
        color = tuple(self.color[:3])
        
        # Convert to bytes for consistent RGB values
        rgb_bytes = rgb_float_to_byte(color)
        
        # Update all the picker values
        context.window_manager.coloraide_picker.mean = color
        context.window_manager.coloraide_picker.current = color
        
        # Update RGB bytes
        context.window_manager.coloraide_picker.mean_r = rgb_bytes[0]
        context.window_manager.coloraide_picker.mean_g = rgb_bytes[1]
        context.window_manager.coloraide_picker.mean_b = rgb_bytes[2]
        
        # Update hex
        context.window_manager.coloraide_picker.hex_color = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        # Calculate and update LAB values
        lab = rgb_to_lab(color)
        context.window_manager.coloraide_picker.lab_l = lab[0]
        context.window_manager.coloraide_picker.lab_a = lab[1]
        context.window_manager.coloraide_picker.lab_b = lab[2]
        
        # Update brush colors
        update_all_colors(color, context)
        
    finally:
        _updating_wheel = False

def update_from_hex(self, context):
    """Update handler for hex color input"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_wheel, _updating_hex
    
    if _updating_lab or _updating_rgb or _updating_picker or _updating_wheel:
        return
    
    if _updating_hex:
        return
    
    _updating_hex = True
    try:
        hex_color = self.hex_color.lstrip('#')
        if len(hex_color) != 6 or not all(c in '0123456789ABCDEFabcdef' for c in hex_color):
            # Reset to black if invalid
            rgb_bytes = (0, 0, 0)
            rgb_float = (0.0, 0.0, 0.0)
            self.hex_color = "#000000"
        else:
            rgb_bytes = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            rgb_float = rgb_byte_to_float(rgb_bytes)
        
        # Update all values
        self.mean = rgb_float
        self.current = rgb_float
        self.mean_r = rgb_bytes[0]
        self.mean_g = rgb_bytes[1]
        self.mean_b = rgb_bytes[2]
        
        # Update wheel
        context.window_manager.coloraide_wheel.color = (*rgb_float, 1.0)
        
        # Update brush colors
        update_all_colors(rgb_float, context)
        
    finally:
        _updating_hex = False

def update_lab(self, context):
    """Update handler for LAB slider changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    if _updating_rgb or _updating_picker or _updating_hex or _updating_wheel:
        return
    
    _updating_lab = True
    try:
        lab = (self.lab_l, self.lab_a, self.lab_b)
        rgb = lab_to_rgb(lab)
        rgb_bytes = rgb_float_to_byte(rgb)
        
        # Update all values
        self.mean = rgb
        self.current = rgb
        self.mean_r = rgb_bytes[0]
        self.mean_g = rgb_bytes[1]
        self.mean_b = rgb_bytes[2]
        
        # Update hex
        self.hex_color = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        # Update wheel
        context.window_manager.coloraide_wheel.color = (*rgb, 1.0)
        
        # Update brush colors
        update_all_colors(rgb, context)
    finally:
        _updating_lab = False

def update_rgb_byte(self, context):
    """Update handler for RGB byte value changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    if _updating_lab or _updating_picker or _updating_hex or _updating_wheel:
        return
        
    _updating_rgb = True
    try:
        rgb_bytes = (
            self.mean_r,
            self.mean_g,
            self.mean_b
        )
        rgb_float = rgb_byte_to_float(rgb_bytes)
        
        # Update all values
        self.mean = rgb_float
        self.current = rgb_float
        
        # Update hex
        self.hex_color = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        # Update wheel
        context.window_manager.coloraide_wheel.color = (*rgb_float, 1.0)
        
        # Calculate and update LAB
        lab = rgb_to_lab(rgb_float)
        self.lab_l = lab[0]
        self.lab_a = lab[1]
        self.lab_b = lab[2]
        
        # Update brush colors
        update_all_colors(rgb_float, context)
    finally:
        _updating_rgb = False

def update_picker_color(self, context):
    """Update handler for picker color changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    if _updating_lab or _updating_rgb or _updating_hex or _updating_wheel:
        return
    
    _updating_picker = True
    try:
        rgb_float = tuple(max(0, min(1, c)) for c in self.mean)
        rgb_bytes = rgb_float_to_byte(rgb_float)
        
        # Update all values
        self.current = rgb_float
        self.mean_r = rgb_bytes[0]
        self.mean_g = rgb_bytes[1]
        self.mean_b = rgb_bytes[2]
        
        # Update hex
        self.hex_color = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        # Update wheel
        context.window_manager.coloraide_wheel.color = (*rgb_float, 1.0)
        
        # Calculate and update LAB
        lab = rgb_to_lab(rgb_float)
        self.lab_l = lab[0]
        self.lab_a = lab[1]
        self.lab_b = lab[2]
        
        # Update brush colors
        update_all_colors(rgb_float, context)
    finally:
        _updating_picker = False

class ColoraidePickerProperties(PropertyGroup):
    """Properties related to the color picker functionality"""
    current: FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        precision=4,
        min=0.0,
        max=1.0,
        description='The current RGB values of the picked pixels',
        subtype='COLOR_GAMMA'
    )
    
    max: FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        precision=4,
        min=0.0,
        max=1.0,
        description='The max RGB values of the picked pixels',
        subtype='COLOR_GAMMA'
    )
    
    min: FloatVectorProperty(
        default=(0.0, 0.0, 0.0),
        precision=4,
        min=0.0,
        max=1.0,
        description='The min RGB values of the picked pixels',
        subtype='COLOR_GAMMA'
    )
    
    median: FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=4,
        min=0.0,
        max=1.0,
        description='The median RGB values of the picked pixels',
        subtype='COLOR_GAMMA'
    )
    
    hex_color: StringProperty(
        name="Hex",
        description="Color in hex format (e.g. #FF0000)",
        default="#808080",
        maxlen=7,
        update=update_from_hex
    )

    # Add RGB byte value properties with update handlers
    mean_r: IntProperty(
        name="R",
        description="Red (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte
    )
    
    mean_g: IntProperty(
        name="G",
        description="Green (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte
    )
    
    mean_b: IntProperty(
        name="B",
        description="Blue (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte
    )
    
    # Add LAB properties with update handlers
    lab_l: FloatProperty(
        name="L",
        description="Lightness (0-100)",
        default=50.0,
        min=0.0,
        max=100.0,
        precision=0,
        update=update_lab
    )
    
    lab_a: FloatProperty(
        name="a",
        description="Green (-) to Red (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=0,
        update=update_lab
    )
    
    lab_b: FloatProperty(
        name="b",
        description="Blue (-) to Yellow (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=0,
        update=update_lab
    )

    # Add mean color property with update handler
    mean: FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=6,
        min=0.0,
        max=1.0,
        description='The mean RGB values of the picked pixels',
        subtype='COLOR_GAMMA',
        update=update_picker_color
    )

class ColoraideDisplayProperties(PropertyGroup):
    """Properties controlling the display settings"""
    show_dynamics: BoolProperty(
        name="Show Color Dynamics",
        default=True
    )
    
    show_rgb_sliders: BoolProperty(
        name="Show RGB Sliders",
        default=True
    )
    
    show_lab_sliders: BoolProperty(
        name="Show LAB Sliders",
        default=True
    )
    
    show_history: BoolProperty(
        name="Show Color History",
        default=True
    )

class ColoraideWheelProperties(PropertyGroup):
    """Properties for the color wheel"""
    scale: FloatProperty(
        name="Wheel Size",
        description="Adjust the size of the color wheel",
        min=1.0,
        max=3.0,
        default=1.5,    
        step=10,
        precision=1
    )
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=update_from_wheel
    )

def register():
    """Register all property groups"""
    bpy.utils.register_class(ColoraidePickerProperties)
    bpy.utils.register_class(ColoraideDisplayProperties)
    bpy.utils.register_class(ColoraideWheelProperties)
    
    # Add to window manager
    bpy.types.WindowManager.coloraide_picker = bpy.props.PointerProperty(type=ColoraidePickerProperties)
    bpy.types.WindowManager.coloraide_display = bpy.props.PointerProperty(type=ColoraideDisplayProperties)
    bpy.types.WindowManager.coloraide_wheel = bpy.props.PointerProperty(type=ColoraideWheelProperties)

def unregister():
    """Unregister all property groups"""
    del bpy.types.WindowManager.coloraide_wheel
    del bpy.types.WindowManager.coloraide_display
    del bpy.types.WindowManager.coloraide_picker
    
    bpy.utils.unregister_class(ColoraideWheelProperties)
    bpy.utils.unregister_class(ColoraideDisplayProperties)
    bpy.utils.unregister_class(ColoraidePickerProperties)