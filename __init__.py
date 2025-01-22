"""
Main initialization file for Coloraide addon.
"""

import bpy

# Import all properties
from .properties.CDYNAMICS_properties import ColoraideDynamicsProperties
from .properties.CHISTORY_properties import ColorHistoryItemProperties, ColoraideHistoryProperties
from .properties.CPICKER_properties import ColoraidePickerProperties
from .properties.CWHEEL_properties import ColoraideWheelProperties
from .properties.HEX_properties import ColoraideHexProperties
from .properties.RGB_properties import ColoraideRGBProperties
from .properties.LAB_properties import ColoraideLABProperties
from .properties.HSV_properties import ColoraideHSVProperties
from .properties.NSAMPLER_properties import ColoraideNormalProperties
from .properties.PALETTE_properties import ColoraidePaletteProperties
from .COLORAIDE_properties import ColoraideDisplayProperties

# Import all operators
from .operators.CDYNAMICS_OT import BRUSH_OT_color_dynamics
from .operators.CHISTORY_OT import COLOR_OT_adjust_history_size, COLOR_OT_clear_history, COLOR_OT_remove_history_color
from .operators.CPICKER_OT import IMAGE_OT_screen_picker, IMAGE_OT_quickpick
from .operators.HEX_OT import COLOR_OT_sync_hex, COLOR_OT_validate_hex
from .operators.NSAMPLER_OT import BRUSH_OT_sample_normal
from .operators.PALETTE_OT import PALETTE_OT_add_color, PALETTE_OT_select_color, PALETTE_OT_remove_color
from .COLORAIDE_monitor import COLOR_OT_monitor

# Import all panels
from .panels.CDYNAMICS_panel import draw_dynamics_panel
from .panels.CHISTORY_panel import draw_history_panel
from .panels.CPICKER_panel import draw_picker_panel
from .panels.CWHEEL_panel import draw_wheel_panel
from .panels.HEX_panel import draw_hex_panel
from .panels.RGB_panel import draw_rgb_panel
from .panels.LAB_panel import draw_lab_panel
from .panels.HSV_panel import draw_hsv_panel
from .panels.NSAMPLER_panel import draw_normal_panel
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
    ColorHistoryItemProperties,
    ColoraideDisplayProperties,
    ColoraideDynamicsProperties,
    ColoraideHistoryProperties,
    ColoraidePickerProperties,
    ColoraideWheelProperties,
    ColoraideHexProperties,
    ColoraideRGBProperties,
    ColoraideLABProperties,
    ColoraideHSVProperties,
    ColoraideNormalProperties,
    ColoraidePaletteProperties,
    
    # Operators
    BRUSH_OT_color_dynamics,
    COLOR_OT_adjust_history_size,
    COLOR_OT_clear_history,
    COLOR_OT_remove_history_color,
    IMAGE_OT_screen_picker,
    IMAGE_OT_quickpick,
    COLOR_OT_sync_hex,
    COLOR_OT_validate_hex,
    BRUSH_OT_sample_normal,
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
    wm = context.window_manager
    
    # Initialize history
    history = wm.coloraide_history.items
    while len(history) > 0:
        history.remove(0)
    
    for _ in range(wm.coloraide_history.size):
        color_item = history.add()
        color_item.color = (0.0, 0.0, 0.0)
    
    # Start color monitor
    if not any(op.bl_idname == "color.monitor" for op in wm.operators):
        bpy.ops.color.monitor('INVOKE_DEFAULT')

def register():
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register property group assignments
    bpy.types.WindowManager.coloraide_history = bpy.props.PointerProperty(type=ColoraideHistoryProperties)
    bpy.types.WindowManager.coloraide_display = bpy.props.PointerProperty(type=ColoraideDisplayProperties)
    bpy.types.WindowManager.coloraide_dynamics = bpy.props.PointerProperty(type=ColoraideDynamicsProperties)
    bpy.types.WindowManager.coloraide_picker = bpy.props.PointerProperty(type=ColoraidePickerProperties)
    bpy.types.WindowManager.coloraide_wheel = bpy.props.PointerProperty(type=ColoraideWheelProperties)
    bpy.types.WindowManager.coloraide_hex = bpy.props.PointerProperty(type=ColoraideHexProperties)
    bpy.types.WindowManager.coloraide_rgb = bpy.props.PointerProperty(type=ColoraideRGBProperties)
    bpy.types.WindowManager.coloraide_lab = bpy.props.PointerProperty(type=ColoraideLABProperties)
    bpy.types.WindowManager.coloraide_hsv = bpy.props.PointerProperty(type=ColoraideHSVProperties)
    bpy.types.WindowManager.coloraide_normal = bpy.props.PointerProperty(type=ColoraideNormalProperties)
    bpy.types.WindowManager.coloraide_palette = bpy.props.PointerProperty(type=ColoraidePaletteProperties)
    
    # Register keymaps
    register_keymaps()
    
    # Initialize addon state
    if bpy.context.window_manager:
        initialize_addon(bpy.context)

def unregister():
    # Unregister keymaps
    unregister_keymaps()
    
    # Unregister property groups
    del bpy.types.WindowManager.coloraide_history
    del bpy.types.WindowManager.coloraide_palette
    del bpy.types.WindowManager.coloraide_normal
    del bpy.types.WindowManager.coloraide_hsv
    del bpy.types.WindowManager.coloraide_lab
    del bpy.types.WindowManager.coloraide_rgb
    del bpy.types.WindowManager.coloraide_hex
    del bpy.types.WindowManager.coloraide_wheel
    del bpy.types.WindowManager.coloraide_picker
    del bpy.types.WindowManager.coloraide_dynamics
    del bpy.types.WindowManager.coloraide_display
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()