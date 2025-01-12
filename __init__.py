# In main __init__.py:

import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatProperty
from math import floor, ceil
from .operators.IMAGE_OT_screen_rect import IMAGE_OT_screen_rect
from .operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from .operators.IMAGE_OT_quickpick import IMAGE_OT_quickpick
from .utils.color_conversions import rgb_to_lab, lab_to_rgb
from .panels.IMAGE_PT_Coloraide_panel import (
    IMAGE_PT_color_picker, 
    VIEW_PT_color_picker, 
    CLIP_PT_color_picker,
    COLOR_OT_adjust_history_size
)

_updating_lab = False
_updating_rgb = False
_updating_picker = False
_updating_hex = False
_updating_wheel = False


bl_info = {
    'name': 'Coloraide',
    'author': 'longiy & Spencer Magnusson',
    'version': (1, 0, 3),
    'blender': (3, 2, 0),
    'location': '(Image Editor, Clip Editor, and 3D View) -> Misc',
    'description': 'Extends color picker with a few extra features',
    'tracker_url': 'https://github.com/semagnum/color-picker-pro/issues',
    'category': 'Generic',
}

class ColorHistoryItem(bpy.types.PropertyGroup):
    def update_color(self, context):
        wm = context.window_manager
        wm.picker_mean = self.color
        wm.picker_current = self.color
        update_all_colors(self.color, context)

    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_color
    )



def rgb_float_to_byte(rgb_float):
    """Convert 0-1 RGB float to 0-255 byte values"""
    return tuple(round(c * 255) for c in rgb_float)

def rgb_byte_to_float(rgb_byte):
    """Convert 0-255 RGB byte values to 0-1 float"""
    return tuple(c / 255 for c in rgb_byte)

def stabilize_lab(lab):
    """Stabilize LAB values using floor/ceil based on sign"""
    L, a, b = lab
    
    # L is always positive, use ceil
    L = ceil(L)
    # For a and b, use ceil for positive, floor for negative
    a = ceil(a) if a >= 0 else floor(a)
    b = ceil(b) if b >= 0 else floor(b)
    
    # Clamp values to valid ranges
    L = max(0, min(100, L))
    a = max(-128, min(127, a))
    b = max(-128, min(127, b))
    
    return (L, a, b)

def update_from_wheel(self, context):
    """Update handler for color wheel changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_hex, _updating_wheel
    if _updating_lab or _updating_rgb or _updating_picker or _updating_hex:
        return
        
    _updating_wheel = True
    try:
        wm = context.window_manager
        # Get RGB values from wheel color
        color = tuple(self.wheel_color[:3])
        
        # Convert to bytes for consistent RGB values
        rgb_bytes = tuple(int(c * 255) for c in color)
        
        # Update all the existing color values without triggering callbacks
        wm["picker_mean_r"] = rgb_bytes[0]
        wm["picker_mean_g"] = rgb_bytes[1]
        wm["picker_mean_b"] = rgb_bytes[2]
        wm["picker_mean"] = color
        wm["picker_current"] = color
        
        # Update hex directly
        wm["hex_color"] = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        # Calculate and update LAB values
        lab = rgb_to_lab(color)
        lab = stabilize_lab(lab)
        wm["lab_l"] = lab[0]
        wm["lab_a"] = lab[1]
        wm["lab_b"] = lab[2]
        
        # Update brush colors
        update_all_colors(color, context)
        
    finally:
        _updating_wheel = False

def update_wheel_from_rgb(self, context):
    """Update color wheel when RGB values change"""
    global _updating_wheel, _updating_rgb, _updating_lab, _updating_picker, _updating_hex
    if _updating_wheel or _updating_rgb or _updating_lab or _updating_picker or _updating_hex:
        return
        
    _updating_wheel = True
    try:
        wm = context.window_manager
        color = wm.picker_mean
        if tuple(wm.wheel_color) != color:
            wm["wheel_color"] = color
    finally:
        _updating_wheel = False

def update_from_hex(self, context):
    """Update handler for hex color input"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_wheel
    
    if _updating_lab or _updating_rgb or _updating_picker or _updating_wheel:
        return
    
    global _updating_hex
    if _updating_hex:
        return
    
    _updating_hex = True
    try:
        hex_color = self.hex_color.lstrip('#')
        if len(hex_color) != 6 or not all(c in '0123456789ABCDEFabcdef' for c in hex_color):
            wm = context.window_manager
            wm["picker_mean_r"] = 0
            wm["picker_mean_g"] = 0
            wm["picker_mean_b"] = 0
            wm["picker_mean"] = (0.0, 0.0, 0.0)
            wm["picker_current"] = (0.0, 0.0, 0.0)
            wm["wheel_color"] = (0.0, 0.0, 0.0, 1.0)  # Add wheel color update
            wm["hex_color"] = "#000000"
            update_all_colors((0.0, 0.0, 0.0), context)
            return
            
        rgb_bytes = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb_float = tuple(c / 255 for c in rgb_bytes)
        
        wm = context.window_manager
        wm["picker_mean_r"] = rgb_bytes[0]
        wm["picker_mean_g"] = rgb_bytes[1]
        wm["picker_mean_b"] = rgb_bytes[2]
        wm["picker_mean"] = rgb_float
        wm["picker_current"] = rgb_float
        wm["wheel_color"] = (*rgb_float, 1.0)  # Add wheel color update
        
        update_all_colors(rgb_float, context)
        
    finally:
        _updating_hex = False

        
def update_lab(self, context):
    """Update handler for LAB slider changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_wheel
    if _updating_rgb or _updating_picker or _updating_wheel:
        return
    
    _updating_lab = True
    try:
        lab = stabilize_lab((self.lab_l, self.lab_a, self.lab_b))
        rgb = lab_to_rgb(lab)
        
        rgb_bytes = tuple(int(c * 255) for c in rgb)
        rgb_float = tuple(c / 255 for c in rgb_bytes)
        
        wm = context.window_manager
        
        wm["picker_mean_r"] = rgb_bytes[0]
        wm["picker_mean_g"] = rgb_bytes[1]
        wm["picker_mean_b"] = rgb_bytes[2]
        
        wm["picker_mean"] = rgb_float
        wm["picker_current"] = rgb_float
        wm["wheel_color"] = (*rgb_float, 1.0)  # Add wheel color update
        
        wm["hex_color"] = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        update_all_colors(rgb_float, context)
    finally:
        _updating_lab = False

def update_rgb_byte(self, context):
    """Update handler for RGB byte value changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_wheel
    if _updating_lab or _updating_picker or _updating_wheel:
        return
        
    _updating_rgb = True
    try:
        wm = context.window_manager
        rgb_bytes = (
            wm.picker_mean_r,
            wm.picker_mean_g,
            wm.picker_mean_b
        )
        
        rgb_float = tuple(c / 255 for c in rgb_bytes)
        
        wm["picker_mean"] = rgb_float
        wm["picker_current"] = rgb_float
        wm["wheel_color"] = (*rgb_float, 1.0)  # Add wheel color update
        
        wm["hex_color"] = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        lab = rgb_to_lab(rgb_float)
        lab = stabilize_lab(lab)
        
        wm["lab_l"] = lab[0]
        wm["lab_a"] = lab[1]
        wm["lab_b"] = lab[2]
        
        update_all_colors(rgb_float, context)
    finally:
        _updating_rgb = False

def update_picker_color(self, context):
    """Update handler for picker color changes"""
    global _updating_lab, _updating_rgb, _updating_picker, _updating_wheel
    if _updating_lab or _updating_rgb or _updating_wheel:
        return
    
    _updating_picker = True
    try:
        wm = context.window_manager
        rgb_float = tuple(max(0, min(1, c)) for c in self.picker_mean)
        
        rgb_bytes = tuple(int(c * 255) for c in rgb_float)
        rgb_float = tuple(c / 255 for c in rgb_bytes)
        
        if tuple(wm.picker_mean) != rgb_float:
            wm["picker_mean"] = rgb_float
        wm["picker_current"] = rgb_float
        wm["wheel_color"] = (*rgb_float, 1.0)  # Add wheel color update
        wm["picker_mean_r"] = rgb_bytes[0]
        wm["picker_mean_g"] = rgb_bytes[1]
        wm["picker_mean_b"] = rgb_bytes[2]
        
        wm["hex_color"] = "#{:02X}{:02X}{:02X}".format(
            rgb_bytes[0],
            rgb_bytes[1],
            rgb_bytes[2]
        )
        
        lab = rgb_to_lab(rgb_float)
        lab = stabilize_lab(lab)
        
        wm["lab_l"] = lab[0]
        wm["lab_a"] = lab[1]
        wm["lab_b"] = lab[2]
        
        update_all_colors(rgb_float, context)
    finally:
        _updating_picker = False

def update_all_colors(color, context):
    """Synchronize color across all relevant brush settings"""
    ts = context.tool_settings
    
    # Update Grease Pencil brush color
    if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
        ts.gpencil_paint.brush.color = color
    
    # Update Texture Paint brush color and unified settings
    if hasattr(ts, 'image_paint') and ts.image_paint.brush:
        ts.image_paint.brush.color = color
        if ts.unified_paint_settings.use_unified_color:
            ts.unified_paint_settings.color = color
        else:
            # If not using unified color, update the active brush
            if context.active_object and context.active_object.mode == 'TEXTURE_PAINT':
                brush = ts.image_paint.brush
                if brush:
                    brush.color = color

classes = [
    ColorHistoryItem,
    COLOR_OT_adjust_history_size,
    IMAGE_OT_screen_picker, 
    IMAGE_OT_screen_rect, 
    IMAGE_OT_quickpick,
    IMAGE_PT_color_picker, 
    VIEW_PT_color_picker, 
    CLIP_PT_color_picker,
]

# Keymap setup
addon_keymaps = []

def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # 3D View keymap
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.quickpick_operator", "BACK_SLASH", "PRESS")
        addon_keymaps.append((km, kmi))

        # Image Editor keymap
        km = kc.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
        kmi = km.keymap_items.new("wm.quickpick_operator", "BACK_SLASH", "PRESS")
        addon_keymaps.append((km, kmi))

        # Clip Editor keymap
        km = kc.keymaps.new(name='Clip', space_type='CLIP_EDITOR')
        kmi = km.keymap_items.new("wm.quickpick_operator", "BACK_SLASH", "PRESS")
        addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # Add window manager properties
    window_manager = bpy.types.WindowManager
    # Initialize history with black swatches
    def init_color_history():
        wm = bpy.context.window_manager
        history = wm.picker_history
        # Clear existing history
        history.clear()
        # Add black swatches up to history_size
        for _ in range(wm.history_size):
            new_color = history.add()
            new_color.color = (0.0, 0.0, 0.0)
            
    # Add wheel scale property
    bpy.types.WindowManager.wheel_scale = FloatProperty(
        name="Wheel Size",
        description="Adjust the size of the color wheel",
        min=1.0,
        max=4.0,
        default=1.5,    
        step=10,
        precision=1
    )
    # Add wheel color property with update handler
    bpy.types.WindowManager.wheel_color = bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=update_from_wheel
    )
    # Add window manager properties
    window_manager.hex_color = bpy.props.StringProperty(
        name="Hex",
        description="Color in hex format (e.g. #FF0000)",
        default="#808080",
        maxlen=7,
        update=update_from_hex
    )
    window_manager.picker_current = bpy.props.FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        precision=4,
        min=0.0,
        max=1.0,
        description='The current RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    window_manager.picker_max = bpy.props.FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        precision=4,
        min=0.0,
        max=1.0,
        description='The max RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    window_manager.picker_min = bpy.props.FloatVectorProperty(
        default=(0.0, 0.0, 0.0),
        precision=4,
        min=0.0,
        max=1.0,
        description='The min RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    window_manager.picker_median = bpy.props.FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=4,
        min=0.0,
        max=1.0,
        description='The median RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    
    # RGB properties in 0-255 range
    window_manager.picker_mean_r = bpy.props.IntProperty(
        name="R",
        description="Red (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte
    )
    window_manager.picker_mean_g = bpy.props.IntProperty(
        name="G",
        description="Green (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte
    )
    window_manager.picker_mean_b = bpy.props.IntProperty(
        name="B",
        description="Blue (0-255)",
        min=0,
        max=255,
        default=128,
        update=update_rgb_byte
    )
    window_manager.picker_mean = bpy.props.FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=6,
        min=0.0,
        max=1.0,
        update=update_picker_color,
        description='The mean RGB values of the picked pixels',
        subtype='COLOR_GAMMA'
    )
    window_manager.custom_size = bpy.props.IntProperty(
        default=10,
        min=1,
        soft_max=100,
        soft_min=5,
        name='Quickpick size',
        description='Custom tile size for Quickpicker (Backlash \ by default)')
    window_manager.history_size = bpy.props.IntProperty(
        default=15,
        min=5,
        max=50,
        name='History Size',
        description='Number of color history slots'
    )
    window_manager.picker_history = bpy.props.CollectionProperty(
        type=ColorHistoryItem,
        name="Color History",
        description="History of recently picked colors"
    )


    register_lab_properties()
    register_keymaps()

    # Initialize color history with black swatches
    try:
        wm = bpy.context.window_manager
        history = wm.picker_history
        
        # Clear any existing history
        while len(history) > 0:
            history.remove(0)
            
        # Add black swatches
        for _ in range(wm.history_size):
            color_item = history.add()
            color_item.color = (0.0, 0.0, 0.0)
    except Exception as e:
        print("Error initializing color history:", e)

def register_lab_properties():
    bpy.types.WindowManager.lab_l = bpy.props.FloatProperty(
        name="L",
        description="Lightness (0-100)",
        default=50.0,
        min=0.0,
        max=100.0,
        precision=0,
        update=update_lab
    )
    
    bpy.types.WindowManager.lab_a = bpy.props.FloatProperty(
        name="a",
        description="Green (-) to Red (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=0,
        update=update_lab
    )
    
    bpy.types.WindowManager.lab_b = bpy.props.FloatProperty(
        name="b",
        description="Blue (-) to Yellow (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=0,
        update=update_lab
    )

def unregister_lab_properties():
    del bpy.types.WindowManager.lab_l
    del bpy.types.WindowManager.lab_a
    del bpy.types.WindowManager.lab_b
    
def unregister():
    unregister_keymaps()
    unregister_lab_properties()
    unregister_wheel_properties()
    
    window_manager = bpy.types.WindowManager
    del window_manager.picker_history
    del window_manager.history_size
    del window_manager.custom_size
    del window_manager.picker_mean
    del window_manager.picker_median
    del window_manager.picker_min
    del window_manager.picker_max
    del window_manager.picker_current    
    del window_manager.picker_mean_r
    del window_manager.picker_mean_g
    del window_manager.picker_mean_b
    
    del bpy.types.WindowManager.wheel_scale
    del bpy.types.WindowManager.wheel_color
    
    del window_manager.hex_color
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()