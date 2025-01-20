"""
Property group definitions for Coloraide addon.
"""

import bpy
from bpy.props import (
    BoolProperty, 
    IntProperty, 
    FloatProperty, 
    FloatVectorProperty,
    StringProperty,
    CollectionProperty,
    PointerProperty,
    EnumProperty
)
from bpy.types import PropertyGroup
from .utils.color_conversions import rgb_to_lab, lab_to_rgb

# Global state flags for update cycle prevention
_updating_lab = False
_updating_rgb = False
_updating_picker = False
_updating_hex = False
_updating_wheel = False
_user_is_editing = False

def is_update_in_progress():
    """Check if any color update cycle is in progress"""
    return any([
        _updating_lab,
        _updating_rgb, 
        _updating_picker,
        _updating_hex,
        _updating_wheel
    ])

def sync_picker_from_brush(context, brush_color):
    """Sync all picker values from brush color without triggering update cycles"""
    global _updating_picker
    _updating_picker = True
    try:
        picker = context.window_manager.coloraide_picker
        
        # Update RGB float values - only update mean, not current
        picker.mean = brush_color
        
        # Update RGB byte values
        rgb_bytes = rgb_float_to_byte(brush_color)
        picker.mean_r = rgb_bytes[0]
        picker.mean_g = rgb_bytes[1]
        picker.mean_b = rgb_bytes[2]
        
        # Update hex
        picker.hex_color = "#{:02X}{:02X}{:02X}".format(*rgb_bytes)
        
        # Update LAB values
        lab = rgb_to_lab(brush_color)
        picker.lab_l = lab[0]
        picker.lab_a = lab[1]
        picker.lab_b = lab[2]
        
        # Update wheel
        context.window_manager.coloraide_wheel.color = (*brush_color, 1.0)
        
    finally:
        _updating_picker = False

def start_user_edit():
    """Start a user editing session"""
    global _user_is_editing
    _user_is_editing = True

def end_user_edit():
    """End a user editing session"""
    global _user_is_editing
    _user_is_editing = False

def rgb_float_to_byte(rgb_float):
    """Convert 0-1 RGB float to 0-255 byte values"""
    return tuple(round(c * 255) for c in rgb_float)

def rgb_byte_to_float(rgb_byte):
    """Convert 0-255 RGB byte values to 0-1 float"""
    return tuple(c / 255 for c in rgb_byte)

def update_all_colors(color, context):
    """Update colors and store originals"""
    ts = context.tool_settings
    
    if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
        ts.gpencil_paint.brush.color = color
    
    if hasattr(ts, 'image_paint') and ts.image_paint.brush:
        ts.image_paint.brush.color = color
        if ts.unified_paint_settings.use_unified_color:
            ts.unified_paint_settings.color = color

def update_lab(self, context):
    """Update handler for LAB slider changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    if _updating_rgb or _updating_picker or _updating_hex or _updating_wheel:
        return
    
    _updating_lab = True
    start_user_edit()
    try:
        lab = (self.lab_l, self.lab_a, self.lab_b)
        rgb = lab_to_rgb(lab)
        rgb_bytes = rgb_float_to_byte(rgb)
        
        # Update only mean values
        self.mean = rgb
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
        end_user_edit()
        _updating_lab = False

def update_from_hex(self, context):
    """Update handler for hex color input"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_wheel, _updating_hex
    
    if _updating_lab or _updating_rgb or _updating_picker or _updating_wheel:
        return
    
    if _updating_hex:
        return
    
    _updating_hex = True
    start_user_edit()
    try:
        hex_color = self.hex_color.lstrip('#')
        if len(hex_color) != 6 or not all(c in '0123456789ABCDEFabcdef' for c in hex_color):
            rgb_bytes = (0, 0, 0)
            rgb_float = (0.0, 0.0, 0.0)
            self.hex_color = "#000000"
        else:
            rgb_bytes = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            rgb_float = rgb_byte_to_float(rgb_bytes)
        
        # Update only mean values
        self.mean = rgb_float
        self.mean_r = rgb_bytes[0]
        self.mean_g = rgb_bytes[1]
        self.mean_b = rgb_bytes[2]
        
        # Update wheel
        context.window_manager.coloraide_wheel.color = (*rgb_float, 1.0)
        
        # Update brush colors
        update_all_colors(rgb_float, context)
    finally:
        end_user_edit()
        _updating_hex = False

def update_from_wheel(self, context):
    """Update handler for color wheel changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    if _updating_lab or _updating_rgb or _updating_picker or _updating_hex:
        return
        
    _updating_wheel = True
    start_user_edit()
    try:
        color = tuple(self.color[:3])
        rgb_bytes = rgb_float_to_byte(color)
        
        picker = context.window_manager.coloraide_picker
        # Update only mean values
        picker.mean = color
        picker.mean_r = rgb_bytes[0]
        picker.mean_g = rgb_bytes[1]
        picker.mean_b = rgb_bytes[2]
        
        # Update hex
        picker.hex_color = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        # Calculate and update LAB values
        lab = rgb_to_lab(color)
        picker.lab_l = lab[0]
        picker.lab_a = lab[1]
        picker.lab_b = lab[2]
        
        # Update brush colors
        update_all_colors(color, context)
    finally:
        end_user_edit()
        _updating_wheel = False

def update_rgb_byte(self, context):
    """Update handler for RGB byte value changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    if _updating_lab or _updating_picker or _updating_hex or _updating_wheel:
        return
        
    _updating_rgb = True
    start_user_edit()
    try:
        rgb_bytes = (self.mean_r, self.mean_g, self.mean_b)
        rgb_float = rgb_byte_to_float(rgb_bytes)
        
        # Update picker values
        context.window_manager.coloraide_picker.mean = rgb_float
        context.window_manager.coloraide_picker.current = rgb_float
        
        # Update hex
        context.window_manager.coloraide_picker.hex_color = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        # Update wheel
        context.window_manager.coloraide_wheel.color = (*rgb_float, 1.0)
        
        # Calculate and update LAB
        lab = rgb_to_lab(rgb_float)
        context.window_manager.coloraide_picker.lab_l = lab[0]
        context.window_manager.coloraide_picker.lab_a = lab[1]
        context.window_manager.coloraide_picker.lab_b = lab[2]
        
        # Update brush colors
        update_all_colors(rgb_float, context)
    finally:
        end_user_edit()
        _updating_rgb = False

def update_picker_color(self, context):
    """Update handler for picker color changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    
    # print("\n=== update_picker_color called ===")
    # print(f"Update flags status:")
    # print(f"_updating_lab: {_updating_lab}")
    # print(f"_updating_rgb: {_updating_rgb}")
    # print(f"_updating_picker: {_updating_picker}")
    # print(f"_updating_hex: {_updating_hex}")
    # print(f"_updating_wheel: {_updating_wheel}")
    
    if _updating_lab or _updating_rgb or _updating_hex or _updating_wheel:
        # print("Update blocked by existing update in progress")
        return
    
    _updating_picker = True
    try:
        # print(f"Processing mean color: {self.mean}")
        rgb_float = tuple(max(0, min(1, c)) for c in self.mean)
        rgb_bytes = rgb_float_to_byte(rgb_float)
        
        # print("Updating values:")
        # print(f"rgb_float: {rgb_float}")
        # print(f"rgb_bytes: {rgb_bytes}")
        
        # Update values
        
        self.mean_r = rgb_bytes[0]
        self.mean_g = rgb_bytes[1]
        self.mean_b = rgb_bytes[2]
        
        # print("Values updated successfully")
        
    finally:
        _updating_picker = False
        # print("update_picker_color complete")

def update_current_color(self, context):
    """Separate update handler for current (1x1 sample) color changes"""
    if is_update_in_progress():
        return
        
    # Only update the current color display without affecting other values
    pass  # The current color will update its UI display automatically

class ColoraideNormalPickerProperties(PropertyGroup):
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
            ('TANGENT', "Tangent Space", "Use tangent space normals (requires UV map)")
        ],
        default='OBJECT'
    )

class ColorHistoryItem(PropertyGroup):
    """Individual color history item"""
    def update_color(self, context):
        wm = context.window_manager
        wm.coloraide_picker.mean = self.color
        wm.coloraide_picker.current = self.color
        ts = context.tool_settings
        
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = self.color
        
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = self.color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = self.color

    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_color
    )

def update_color_dynamics(self, context):
    """Update color dynamics when strength changes"""
    if self.strength > 0:
        if not any(op.bl_idname == "brush.color_dynamics" for op in context.window_manager.operators):
            bpy.ops.brush.color_dynamics('INVOKE_DEFAULT')
    else:
        context.window_manager.color_dynamics.running = False

class ColoraideDynamicsProperties(PropertyGroup):
    running: BoolProperty(
        name="Color Dynamics Running",
        default=True
    )
    
    strength: IntProperty(
        name="Strength",
        description="Amount of random color variation during strokes",
        min=0,
        max=100,
        default=0,
        subtype='PERCENTAGE',
        update=update_color_dynamics
    )

class ColoraideHistoryProperties(PropertyGroup):
    size: IntProperty(
        default=8,
        min=8,
        max=80,
        name='History Size',
        description='Number of color history slots'
    )
    
    items: CollectionProperty(
        type=ColorHistoryItem,
        name="Color History",
        description="History of recently picked colors"
    )

class ColoraidePickerProperties(PropertyGroup):
    def _update_mean(self, context):
        """Combined update handler for mean color changes"""
        # print("\n=== _update_mean called ===")
        # print(f"Color being set: {self.mean}")
        start_user_edit()
        try:
            update_picker_color(self, context)
        finally:
            end_user_edit()
            
    def _update_current(self, context):
        """Combined update handler for current color changes"""
        start_user_edit()
        try:
            update_current_color(self, context)
        finally:
            end_user_edit()
    
    
    
    custom_size: IntProperty(
        default=10,
        min=1,
        soft_max=100,
        soft_min=5,
        name='Quickpick Size',
        description='Custom tile size for Quickpicker (Backlash \\ by default)'
    )
    
    mean: FloatVectorProperty(
        name="Mean Color",
        default=(0.5, 0.5, 0.5),
        precision=6,
        min=0.0,
        max=1.0,
        description='The mean RGB values of the picked pixels',
        subtype='COLOR_GAMMA',
        update=_update_mean
    )
    
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
    
    show_palettes: BoolProperty(
        name="Show Color Palettes",
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


