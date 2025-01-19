"""
Main initialization file for Coloraide addon.
"""

import bpy
import random
import time

from bpy.types import PropertyGroup
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
from math import floor, ceil

from .properties import (
    ColorHistoryItem,
    ColoraideDynamicsProperties,  
    ColoraideHistoryProperties,
    ColoraidePickerProperties,
    ColoraideDisplayProperties, 
    ColoraideWheelProperties,
    ColoraideNormalPickerProperties,

)
from .operators.COLOR_OT_monitor import COLOR_OT_monitor
from .operators.BRUSH_OT_normal_color_picker import BRUSH_OT_normal_color_picker  
from .operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from .operators.IMAGE_OT_quickpick import IMAGE_OT_quickpick
from .utils.color_conversions import rgb_to_lab, lab_to_rgb
from .operators.BRUSH_OT_color_dynamics import BRUSH_OT_color_dynamics
from .panels.IMAGE_PT_Coloraide_panel import (
    IMAGE_PT_color_picker, 
    VIEW_PT_color_picker, 
    CLIP_PT_color_picker,
    COLOR_OT_adjust_history_size,
    PAINT_OT_add_palette_color,
    PALETTE_OT_select_color
)

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

classes = [
    # Property Groups (register first)
    ColorHistoryItem,
    ColoraideDynamicsProperties,
    ColoraideHistoryProperties,
    ColoraidePickerProperties,
    ColoraideDisplayProperties,
    ColoraideWheelProperties,
    ColoraideNormalPickerProperties,
    
    # Operators (register second)
    COLOR_OT_monitor,
    PALETTE_OT_select_color,
    PAINT_OT_add_palette_color,  
    COLOR_OT_adjust_history_size,
    IMAGE_OT_screen_picker, 
    IMAGE_OT_quickpick,
    BRUSH_OT_color_dynamics,
    BRUSH_OT_normal_color_picker,
    
    # Panels (register last)
    IMAGE_PT_color_picker, 
    VIEW_PT_color_picker, 
    CLIP_PT_color_picker,
]

# Keymap setup
addon_keymaps = []

def initialize_color_history():
    """Separate function for color history initialization"""
    try:
        wm = bpy.context.window_manager
        history = wm.color_history.items
        if wm.color_dynamics.strength > 0:
            bpy.ops.brush.color_dynamics('INVOKE_DEFAULT')
            
        while len(history) > 0:
            history.remove(0)
            
        for _ in range(wm.color_history.size):
            color_item = history.add()
            color_item.color = (0.0, 0.0, 0.0)
    except Exception as e:
        print("Error initializing color history:", e)

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
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register property assignments
    window_manager = bpy.types.WindowManager
    window_manager.coloraide_picker = PointerProperty(type=ColoraidePickerProperties)
    window_manager.coloraide_display = PointerProperty(type=ColoraideDisplayProperties)
    window_manager.coloraide_wheel = PointerProperty(type=ColoraideWheelProperties)
    window_manager.color_dynamics = PointerProperty(type=ColoraideDynamicsProperties)
    window_manager.color_history = PointerProperty(type=ColoraideHistoryProperties)
    window_manager.normal_picker = PointerProperty(type=ColoraideNormalPickerProperties)

    # Register keymaps
    register_keymaps()

    # Initialize color history
    initialize_color_history()

    # Start the monitor using a timer
    bpy.app.timers.register(start_color_monitor, first_interval=0.1)

# Add this new function
def start_color_monitor():
    """Start the color monitor with a delay to ensure context is ready"""
    try:
        if bpy.context and bpy.context.window_manager:
            bpy.ops.color.monitor('INVOKE_DEFAULT')
            return None  # Unregister the timer
        return 0.1  # Try again in 0.1 seconds
    except Exception as e:
        print(f"Error starting color monitor: {e}")
        return None  # Unregister the timer on error



def unregister():

    # Unregister keymaps
    unregister_keymaps()
    
    # Remove properties
    window_manager = bpy.types.WindowManager
    del window_manager.color_history
    del window_manager.color_dynamics
    del window_manager.coloraide_wheel
    del window_manager.coloraide_display
    del window_manager.coloraide_picker
    del window_manager.normal_picker

    # Unregister classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()

