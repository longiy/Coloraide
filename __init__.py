# In main __init__.py:

import bpy
from bpy.props import FloatProperty  # Add this import
from .operators.IMAGE_OT_screen_rect import IMAGE_OT_screen_rect
from .operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from .operators.IMAGE_OT_quickpick import IMAGE_OT_quickpick
from .utils.color_conversions import rgb_to_lab, lab_to_rgb
from .panels.IMAGE_PT_Coloraide_panel import (
    IMAGE_PT_color_picker, 
    VIEW_PT_color_picker, 
    CLIP_PT_color_picker,
    COLOR_OT_adjust_history_size  # Add this line
)

_updating_lab = False
_updating_rgb = False
_updating_picker = False

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

# Define ColorHistoryItem only once, in main __init__.py
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

def round_lab(lab_values):
    """Round LAB values to reasonable precision"""
    L, a, b = lab_values
    return (round(L, 1), round(a, 1), round(b, 1))

def update_lab(self, context):
    """Update handler for LAB slider changes"""
    global _updating_lab, _updating_rgb, _updating_picker
    if _updating_rgb or _updating_picker:
        return
    
    _updating_lab = True
    try:
        # Get and round LAB values
        lab = round_lab((self.lab_l, self.lab_a, self.lab_b))
        rgb = lab_to_rgb(lab)
        
        # Convert to bytes and back for consistent rounding
        rgb_bytes = rgb_float_to_byte(rgb)
        rgb_float = rgb_byte_to_float(rgb_bytes)
        
        # Update all values without triggering their update callbacks
        wm = context.window_manager
        
        # Update RGB byte values first (0-255)
        wm["picker_mean_r"] = rgb_bytes[0]
        wm["picker_mean_g"] = rgb_bytes[1]
        wm["picker_mean_b"] = rgb_bytes[2]
        
        # Then update float RGB values (0-1)
        wm["picker_mean"] = rgb_float
        wm["picker_current"] = rgb_float
        
        # Update brush colors
        update_all_colors(rgb_float, context)
    finally:
        _updating_lab = False

def update_lab(self, context):
    """Update handler for LAB slider changes"""
    global _updating_lab, _updating_rgb, _updating_picker
    if _updating_rgb or _updating_picker:
        return
    
    _updating_lab = True
    try:
        # Get and round LAB values
        lab = round_lab((self.lab_l, self.lab_a, self.lab_b))
        rgb = lab_to_rgb(lab)
        
        # Convert to bytes and back for consistent rounding
        rgb_bytes = rgb_float_to_byte(rgb)
        rgb_float = rgb_byte_to_float(rgb_bytes)
        
        # Update all values without triggering their update callbacks
        wm = context.window_manager
        
        # Update RGB byte values first (0-255)
        wm["picker_mean_r"] = rgb_bytes[0]
        wm["picker_mean_g"] = rgb_bytes[1]
        wm["picker_mean_b"] = rgb_bytes[2]
        
        # Then update float RGB values (0-1)
        wm["picker_mean"] = rgb_float
        wm["picker_current"] = rgb_float
        
        # Update brush colors
        update_all_colors(rgb_float, context)
    finally:
        _updating_lab = False

def update_picker_color(self, context):
    """Update handler for picker color changes"""
    global _updating_lab, _updating_rgb, _updating_picker
    if _updating_lab or _updating_rgb:
        return
    
    _updating_picker = True
    try:
        # Convert RGB values to byte values and back for consistent rounding
        rgb_float = tuple(self.picker_mean)
        rgb_bytes = rgb_float_to_byte(rgb_float)
        rgb = rgb_byte_to_float(rgb_bytes)
        
        # Update brush colors
        update_all_colors(rgb, context)
        
        # Update LAB values
        lab = rgb_to_lab(rgb)
        lab = round_lab(lab)
        
        # Update values without triggering updates
        wm = context.window_manager
        wm["lab_l"] = lab[0]
        wm["lab_a"] = lab[1]
        wm["lab_b"] = lab[2]
        wm["picker_mean"] = rgb
        wm["picker_current"] = rgb
    finally:
        _updating_picker = False

def update_all_colors(color, context):
    """
    Synchronize color across all relevant brush settings
    """
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

# List of classes to register (remove ColorHistoryItem from panels/__init__.py)
classes = [
    ColorHistoryItem,
    COLOR_OT_adjust_history_size,  # Add this line
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
    
    # Keep the original float property for internal use
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
    
    register_lab_properties()  # Add this line
    # Register all classes
    
    register_keymaps()

def register_lab_properties():
        # Update LAB property definitions
    bpy.types.WindowManager.lab_l = bpy.props.FloatProperty(
        name="L",
        description="Lightness (0-100)",
        default=50.0,
        min=0.0,
        max=100.0,
        precision=0,  # One decimal place for LAB
        update=update_lab
    )
    
    bpy.types.WindowManager.lab_a = bpy.props.FloatProperty(
        name="a",
        description="Green (-) to Red (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=0,  # One decimal place for LAB
        update=update_lab
    )
    
    bpy.types.WindowManager.lab_b = bpy.props.FloatProperty(
        name="b",
        description="Blue (-) to Yellow (+)",
        default=0.0,
        min=-128.0,
        max=127.0,
        precision=0,  # One decimal place for LAB
        update=update_lab
    )
def update_rgb_byte(self, context):
    """Update handler for RGB byte value changes (0-255 range)"""
    global _updating_lab, _updating_rgb, _updating_picker
    if _updating_lab or _updating_picker:
        return
        
    _updating_rgb = True
    try:
        wm = context.window_manager
        # Convert byte values to float
        rgb = (
            wm.picker_mean_r / 255.0,
            wm.picker_mean_g / 255.0,
            wm.picker_mean_b / 255.0
        )
        
        # Update the float RGB values
        wm["picker_mean"] = rgb
        wm["picker_current"] = rgb
        
        # Update LAB values
        lab = rgb_to_lab(rgb)
        lab = round_lab(lab)
        wm["lab_l"] = lab[0]
        wm["lab_a"] = lab[1]
        wm["lab_b"] = lab[2]
        
        # Update brush colors
        update_all_colors(rgb, context)
    finally:
        _updating_rgb = False

def update_picker_color(self, context):
    global _updating_lab, _updating_rgb, _updating_picker
    if _updating_lab or _updating_rgb:
        return
    
def unregister_lab_properties():
    del bpy.types.WindowManager.lab_l
    del bpy.types.WindowManager.lab_a
    del bpy.types.WindowManager.lab_b
    
def unregister():
    unregister_keymaps()
    unregister_lab_properties()  # Add this line
    # Remove window manager properties
    window_manager = bpy.types.WindowManager
    del window_manager.picker_history
    del window_manager.history_size  # Add this line
    del window_manager.custom_size
    del window_manager.picker_mean
    del window_manager.picker_median
    del window_manager.picker_min
    del window_manager.picker_max
    del window_manager.picker_current    
    
    del window_manager.picker_mean_r
    del window_manager.picker_mean_g
    del window_manager.picker_mean_b
    del window_manager.picker_mean
    
    # Unregister all classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()