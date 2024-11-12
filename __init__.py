# In main __init__.py:

import bpy
from .operators.IMAGE_OT_screen_rect import IMAGE_OT_screen_rect
from .operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from .operators.IMAGE_OT_quickpick import IMAGE_OT_quickpick
from .panels import (
    IMAGE_PT_color_picker, 
    VIEW_PT_color_picker, 
    CLIP_PT_color_picker,
    COLOR_OT_adjust_history_size  # Add this line
)

bl_info = {
    'name': 'Color Picker Pro',
    'author': 'Spencer Magnusson',
    'version': (1, 0, 4),
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
        # Update the brush colors
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
    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add window manager properties
    window_manager = bpy.types.WindowManager
    window_manager.picker_current = bpy.props.FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        precision=4,
        description='The current RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    window_manager.picker_max = bpy.props.FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        precision=4,
        description='The max RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    window_manager.picker_min = bpy.props.FloatVectorProperty(
        default=(0.0, 0.0, 0.0),
        precision=4,
        description='The min RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    window_manager.picker_median = bpy.props.FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=4,
        description='The median RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    window_manager.picker_mean = bpy.props.FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=4,
        description='The mean RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    window_manager.custom_size = bpy.props.IntProperty(
        default=10,
        min=1,
        soft_max=100,
        soft_min=5,
        name='Quickpick size',
        description='Custom tile size for Quickpicker (Backlash \ by default)')
     # Add new history_size property
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
    
    register_keymaps()

def unregister():
    unregister_keymaps()
    
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
    
    # Unregister all classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()