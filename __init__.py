"""
Main initialization file for Coloraide addon.
"""

import bpy
import random
import time
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatProperty
from math import floor, ceil

from .properties import register as register_properties, unregister as unregister_properties
from .operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from .operators.IMAGE_OT_quickpick import IMAGE_OT_quickpick
from .utils.color_conversions import rgb_to_lab, lab_to_rgb
from .operators.BRUSH_OT_color_dynamics import BRUSH_OT_color_dynamics
from .panels.IMAGE_PT_Coloraide_panel import (
    IMAGE_PT_color_picker, 
    VIEW_PT_color_picker, 
    CLIP_PT_color_picker,
    COLOR_OT_adjust_history_size
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
    COLOR_OT_adjust_history_size,
    IMAGE_OT_screen_picker, 
    IMAGE_OT_quickpick,
    BRUSH_OT_color_dynamics,
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
    # Register property groups first
    register_properties()
    
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register keymaps
    register_keymaps()

    # Initialize color history
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

def unregister():
    unregister_keymaps()
    
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    # Unregister property groups last
    unregister_properties()

if __name__ == '__main__':
    register()