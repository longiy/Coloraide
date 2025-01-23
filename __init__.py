"""
Main initialization file for Coloraide addon.
"""
import bpy

# First utilities and sync system from root
from .COLORAIDE_utils import *
from .COLORAIDE_sync import sync_all, update_manager 

# Import all properties
from .properties.CPICKER_properties import ColoraidePickerProperties
from .properties.CWHEEL_properties import ColoraideWheelProperties 
from .properties.HEX_properties import ColoraideHexProperties
from .properties.RGB_properties import ColoraideRGBProperties
from .properties.LAB_properties import ColoraideLABProperties
from .properties.HSV_properties import ColoraideHSVProperties
from .properties.CHISTORY_properties import ColoraideHistoryProperties, ColorHistoryItemProperties
from .properties.NSAMPLER_properties import ColoraideNormalProperties
from .properties.CDYNAMICS_properties import ColoraideDynamicsProperties
from .COLORAIDE_properties import ColoraideDisplayProperties

# Import all operators
from .operators.CPICKER_OT import IMAGE_OT_screen_picker, IMAGE_OT_quickpick
from .operators.HEX_OT import COLOR_OT_sync_hex, COLOR_OT_validate_hex
from .operators.HSV_OT import COLOR_OT_sync_hsv  
from .operators.RGB_OT import COLOR_OT_sync_rgb
from .operators.LAB_OT import COLOR_OT_sync_lab
from .operators.CWHEEL_OT import COLOR_OT_sync_wheel, COLOR_OT_reset_wheel_scale
from .operators.CHISTORY_OT import COLOR_OT_adjust_history_size, COLOR_OT_clear_history, COLOR_OT_remove_history_color
from .operators.NSAMPLER_OT import BRUSH_OT_sample_normal
from .operators.CDYNAMICS_OT import BRUSH_OT_color_dynamics
from .operators.PALETTE_OT import PALETTE_OT_add_color, PALETTE_OT_select_color, PALETTE_OT_remove_color
from .COLORAIDE_monitor import COLOR_OT_monitor

# Import all panels
from .panels.CPICKER_panel import draw_picker_panel
from .panels.CWHEEL_panel import draw_wheel_panel  
from .panels.HEX_panel import draw_hex_panel
from .panels.RGB_panel import draw_rgb_panel
from .panels.LAB_panel import draw_lab_panel
from .panels.HSV_panel import draw_hsv_panel
from .panels.CHISTORY_panel import draw_history_panel
from .panels.NSAMPLER_panel import draw_normal_panel
from .panels.CDYNAMICS_panel import draw_dynamics_panel
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

# Keymap storage
addon_keymaps = []

def register_keymaps():
    """Register addon keymaps"""
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # 3D View keymap
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("image.quickpick", "BACK_SLASH", "PRESS")
        addon_keymaps.append((km, kmi))

        # Image Editor keymap
        km = kc.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
        kmi = km.keymap_items.new("image.quickpick", "BACK_SLASH", "PRESS")
        addon_keymaps.append((km, kmi))

        # Clip Editor keymap
        km = kc.keymaps.new(name='Clip', space_type='CLIP_EDITOR')
        kmi = km.keymap_items.new("image.quickpick", "BACK_SLASH", "PRESS")
        addon_keymaps.append((km, kmi))

def unregister_keymaps():
    """Unregister addon keymaps"""
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

# Collect all classes that need registration
classes = [
    # Properties
    ColoraideDisplayProperties,
    ColoraidePickerProperties,
    ColoraideWheelProperties,
    ColoraideHexProperties,
    ColoraideRGBProperties,
    ColoraideLABProperties,
    ColoraideHSVProperties,
    ColorHistoryItemProperties,  # Register before ColoraideHistoryProperties
    ColoraideHistoryProperties,
    ColoraideNormalProperties,
    ColoraideDynamicsProperties,
    
    # Operators
    IMAGE_OT_screen_picker,
    IMAGE_OT_quickpick,
    COLOR_OT_sync_hex,
    COLOR_OT_validate_hex,
    COLOR_OT_sync_hsv,
    COLOR_OT_sync_rgb,
    COLOR_OT_sync_lab,
    COLOR_OT_sync_wheel,
    COLOR_OT_reset_wheel_scale,
    COLOR_OT_adjust_history_size,
    COLOR_OT_clear_history,
    COLOR_OT_remove_history_color,
    BRUSH_OT_sample_normal,
    BRUSH_OT_color_dynamics,
    PALETTE_OT_add_color,
    PALETTE_OT_select_color,
    PALETTE_OT_remove_color,
    COLOR_OT_monitor,
    
    # Panels
    IMAGE_PT_coloraide,
    VIEW3D_PT_coloraide,
    CLIP_PT_coloraide,
]

def initialize_addon(context):
    """Initialize addon state after registration"""
    if context and context.window_manager:
        # Initialize color history
        if hasattr(context.window_manager, 'coloraide_history'):
            context.window_manager.coloraide_history.initialize_history()
            
        # Start color monitor
        bpy.ops.color.monitor('INVOKE_DEFAULT')


def register():
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register property group assignments
    bpy.types.WindowManager.coloraide_display = bpy.props.PointerProperty(type=ColoraideDisplayProperties)
    bpy.types.WindowManager.coloraide_picker = bpy.props.PointerProperty(type=ColoraidePickerProperties)
    bpy.types.WindowManager.coloraide_wheel = bpy.props.PointerProperty(type=ColoraideWheelProperties)
    bpy.types.WindowManager.coloraide_hex = bpy.props.PointerProperty(type=ColoraideHexProperties)
    bpy.types.WindowManager.coloraide_rgb = bpy.props.PointerProperty(type=ColoraideRGBProperties)
    bpy.types.WindowManager.coloraide_lab = bpy.props.PointerProperty(type=ColoraideLABProperties)
    bpy.types.WindowManager.coloraide_hsv = bpy.props.PointerProperty(type=ColoraideHSVProperties)
    bpy.types.WindowManager.coloraide_history = bpy.props.PointerProperty(type=ColoraideHistoryProperties)
    bpy.types.WindowManager.coloraide_normal = bpy.props.PointerProperty(type=ColoraideNormalProperties)
    bpy.types.WindowManager.coloraide_dynamics = bpy.props.PointerProperty(type=ColoraideDynamicsProperties)
    
    # Register keymaps
    register_keymaps()
    
    # Use timer to initialize after context is ready
    bpy.app.timers.register(lambda: initialize_addon(bpy.context) if bpy.context else None, first_interval=0.1)

def unregister():
    # Unregister keymaps
    unregister_keymaps()
    
    # Unregister property groups
    del bpy.types.WindowManager.coloraide_dynamics
    del bpy.types.WindowManager.coloraide_normal
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