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
from .operators.IMAGE_OT_screen_rect import IMAGE_OT_screen_rect
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

class ColorHistoryItem(bpy.types.PropertyGroup):
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

    color: bpy.props.FloatVectorProperty(
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
    if self.color_dynamics_strength > 0:
        if not any(op.bl_idname == "brush.color_dynamics" for op in context.window_manager.operators):
            bpy.ops.brush.color_dynamics('INVOKE_DEFAULT')
    else:
        context.window_manager.color_dynamics_running = False

classes = [
    ColorHistoryItem,
    COLOR_OT_adjust_history_size,
    IMAGE_OT_screen_picker, 
    IMAGE_OT_screen_rect, 
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

    # Register remaining individual properties
    window_manager = bpy.types.WindowManager
    
    # Color dynamics properties
    window_manager.color_dynamics_running = bpy.props.BoolProperty(
        name="Color Dynamics Running",
        default=True
    )
    
    window_manager.color_dynamics_strength = bpy.props.IntProperty(
        name="Strength",
        description="Amount of random color variation during strokes",
        min=0,
        max=100,
        default=0,
        subtype='PERCENTAGE',
        update=update_color_dynamics
    )
    
    # History properties
    window_manager.history_size = bpy.props.IntProperty(
        default=8,
        min=8,
        max=80,
        name='History Size',
        description='Number of color history slots'
    )
    
    window_manager.picker_history = bpy.props.CollectionProperty(
        type=ColorHistoryItem,
        name="Color History",
        description="History of recently picked colors"
    )

    window_manager.custom_size = bpy.props.IntProperty(
        default=10,
        min=1,
        soft_max=100,
        soft_min=5,
        name='Quickpick Size',
        description='Custom tile size for Quickpicker (Backlash \\ by default)'
    )

    # Register keymaps
    register_keymaps()

    # Initialize color history
    try:
        wm = bpy.context.window_manager
        history = wm.picker_history
        if wm.color_dynamics_strength > 0:
            bpy.ops.brush.color_dynamics('INVOKE_DEFAULT')
            
        while len(history) > 0:
            history.remove(0)
            
        for _ in range(wm.history_size):
            color_item = history.add()
            color_item.color = (0.0, 0.0, 0.0)
    except Exception as e:
        print("Error initializing color history:", e)

def unregister():
    unregister_keymaps()
    
    # Unregister remaining individual properties
    window_manager = bpy.types.WindowManager
    del window_manager.picker_history
    del window_manager.history_size
    del window_manager.custom_size
    del window_manager.color_dynamics_strength
    del window_manager.color_dynamics_running
    
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    # Unregister property groups last
    unregister_properties()

if __name__ == '__main__':
    register()