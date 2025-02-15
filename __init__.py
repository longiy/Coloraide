"""
Main initialization file for Coloraide addon.
"""
import bpy
from bpy.app.handlers import persistent

# First utilities and sync system from root
from .COLORAIDE_utils import *
from .COLORAIDE_sync import sync_all, is_updating, update_lock
from .COLORAIDE_keymaps import register_keymaps, unregister_keymaps
from .COLORAIDE_brush_sync import (sync_picker_from_brush, sync_brush_from_picker, 
                                 update_brush_color, is_brush_updating)

# Import all properties
from .properties.PALETTE_properties import ColoraidePaletteProperties
from .properties.NORMAL_properties import ColoraideNormalProperties
from .properties.CDYNAMICS_properties import ColoraideDynamicsProperties
from .properties.CPICKER_properties import ColoraidePickerProperties
from .properties.CWHEEL_properties import ColoraideWheelProperties 
from .properties.HEX_properties import ColoraideHexProperties
from .properties.RGB_properties import ColoraideRGBProperties
from .properties.LAB_properties import ColoraideLABProperties
from .properties.HSV_properties import ColoraideHSVProperties
from .properties.CHISTORY_properties import ColoraideHistoryProperties, ColorHistoryItemProperties
from .COLORAIDE_properties import ColoraideDisplayProperties

# Import all operators and panels
from .operators.NORMAL_OT import NORMAL_OT_color_picker
from .operators.CDYNAMICS_OT import COLOR_OT_color_dynamics
from .operators.CPICKER_OT import IMAGE_OT_screen_picker, IMAGE_OT_quickpick
from .operators.HSV_OT import COLOR_OT_sync_hsv  
from .operators.RGB_OT import COLOR_OT_sync_rgb
from .operators.LAB_OT import COLOR_OT_sync_lab
from .operators.CWHEEL_OT import COLOR_OT_sync_wheel, COLOR_OT_reset_wheel_scale
from .operators.CHISTORY_OT import COLOR_OT_adjust_history_size, COLOR_OT_clear_history
from .operators.PALETTE_OT import PALETTE_OT_add_color, PALETTE_OT_remove_color
from .COLORAIDE_monitor import COLOR_OT_monitor
from .operators.HEX_OT import COLOR_OT_sync_hex

# Import all panels
from .panels.NORMAL_panel import draw_normal_panel
from .panels.CDYNAMICS_panel import draw_dynamics_panel
from .panels.CPICKER_panel import draw_picker_panel
from .panels.CWHEEL_panel import draw_wheel_panel  
from .panels.HEX_panel import draw_hex_panel
from .panels.RGB_panel import draw_rgb_panel
from .panels.LAB_panel import draw_lab_panel
from .panels.HSV_panel import draw_hsv_panel
from .panels.CHISTORY_panel import draw_history_panel
from .panels.PALETTE_panel import draw_palette_panel
from .COLORAIDE_panel import IMAGE_PT_coloraide, VIEW3D_PT_coloraide, CLIP_PT_coloraide

bl_info = {
    'name': 'Coloraide',
    'author': 'longiy',
    'version': (1, 2, 8),
    'blender': (4, 0, 0),
    'location': '(Image Editor, Clip Editor, and 3D View) -> Color',
    'description': 'Advanced color picker with extended features',
    'warning': '',
    'doc_url': '',
    'category': 'Paint',
}

# Collect all classes that need registration
classes = [
    # Properties
    ColoraidePaletteProperties,
    ColoraideNormalProperties,
    ColoraideDynamicsProperties,
    ColoraideDisplayProperties,
    ColoraidePickerProperties,
    ColoraideWheelProperties,
    ColoraideHexProperties,
    ColoraideRGBProperties,
    ColoraideLABProperties,
    ColoraideHSVProperties,
    ColorHistoryItemProperties,  # Register before ColoraideHistoryProperties
    ColoraideHistoryProperties,
    
    # Operators
    NORMAL_OT_color_picker,
    IMAGE_OT_screen_picker,
    IMAGE_OT_quickpick,
    COLOR_OT_sync_hex,
    COLOR_OT_sync_hsv,
    COLOR_OT_sync_rgb,
    COLOR_OT_sync_lab,
    COLOR_OT_sync_wheel,
    COLOR_OT_reset_wheel_scale,
    COLOR_OT_adjust_history_size,
    COLOR_OT_clear_history,
    PALETTE_OT_add_color,
    PALETTE_OT_remove_color,
    COLOR_OT_monitor,
    COLOR_OT_color_dynamics,
    
    # Panels
    IMAGE_PT_coloraide,
    VIEW3D_PT_coloraide,
    CLIP_PT_coloraide,
]

def start_color_monitor():
    """Start the color monitor modal operator"""
    bpy.ops.color.monitor('INVOKE_DEFAULT')
    return None  # Important: Return None to prevent timer error

@persistent
def load_handler(dummy):
    """Ensure color monitor is running after file load"""
    # Small delay to ensure context is ready
    bpy.app.timers.register(start_color_monitor, first_interval=0.1)

def initialize_addon(context):
    """Initialize addon state after registration"""
    if context and context.window_manager:
        # Initialize color history
        if hasattr(context.window_manager, 'coloraide_history'):
            context.window_manager.coloraide_history.initialize_history()

def register():
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
        
    # Register keymaps
    register_keymaps()
    
    # Register property group assignments
    bpy.types.WindowManager.coloraide_palette = bpy.props.PointerProperty(type=ColoraidePaletteProperties)
    bpy.types.WindowManager.coloraide_normal = bpy.props.PointerProperty(type=ColoraideNormalProperties)
    bpy.types.WindowManager.coloraide_dynamics = bpy.props.PointerProperty(type=ColoraideDynamicsProperties)
    bpy.types.WindowManager.coloraide_display = bpy.props.PointerProperty(type=ColoraideDisplayProperties)
    bpy.types.WindowManager.coloraide_picker = bpy.props.PointerProperty(type=ColoraidePickerProperties)
    bpy.types.WindowManager.coloraide_wheel = bpy.props.PointerProperty(type=ColoraideWheelProperties)
    bpy.types.WindowManager.coloraide_hex = bpy.props.PointerProperty(type=ColoraideHexProperties)
    bpy.types.WindowManager.coloraide_rgb = bpy.props.PointerProperty(type=ColoraideRGBProperties)
    bpy.types.WindowManager.coloraide_lab = bpy.props.PointerProperty(type=ColoraideLABProperties)
    bpy.types.WindowManager.coloraide_hsv = bpy.props.PointerProperty(type=ColoraideHSVProperties)
    bpy.types.WindowManager.coloraide_history = bpy.props.PointerProperty(type=ColoraideHistoryProperties)
    
    # Add load handler
    bpy.app.handlers.load_post.append(load_handler)
    
    # Initialize addon
    initialize_addon(bpy.context)
    
    # Start color monitor after slight delay
    bpy.app.timers.register(start_color_monitor, first_interval=0.1)

def unregister():
    # Remove load handler
    bpy.app.handlers.load_post.remove(load_handler)
    
    # Unregister keymaps
    unregister_keymaps()
    
    # Unregister property groups
    del bpy.types.WindowManager.coloraide_palette
    del bpy.types.WindowManager.coloraide_normal
    del bpy.types.WindowManager.coloraide_dynamics
    del bpy.types.WindowManager.coloraide_history
    del bpy.types.WindowManager.coloraide_hsv
    del bpy.types.WindowManager.coloraide_lab
    del bpy.types.WindowManager.coloraide_rgb
    del bpy.types.WindowManager.coloraide_hex
    del bpy.types.WindowManager.coloraide_wheel
    del bpy.types.WindowManager.coloraide_picker
    del bpy.types.WindowManager.coloraide_display
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()