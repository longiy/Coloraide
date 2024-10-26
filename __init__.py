import bpy
from .operators.IMAGE_OT_screen_rect import IMAGE_OT_screen_rect
from .operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from .operators.IMAGE_OT_quickpick import IMAGE_OT_quickpick
from .panels import IMAGE_PT_color_picker, VIEW_PT_color_picker, CLIP_PT_color_picker

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

# Classes to register
classes = [IMAGE_OT_screen_picker, IMAGE_OT_screen_rect, IMAGE_OT_quickpick,
           IMAGE_PT_color_picker, VIEW_PT_color_picker, CLIP_PT_color_picker]

# Define WindowManager Properties
window_manager_props = [
    ('picker_current', bpy.props.FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        precision=4,
        description='The current RGB values of the picked pixels',
        subtype='COLOR_GAMMA')),        
    ('picker_max', bpy.props.FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        precision=4,
        description='The max RGB values of the picked pixels',
        subtype='COLOR_GAMMA')),
    ('picker_min', bpy.props.FloatVectorProperty(
        default=(0.0, 0.0, 0.0),
        precision=4,
        description='The min RGB values of the picked pixels',
        subtype='COLOR_GAMMA')),
    ('picker_median', bpy.props.FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=4,
        description='The median RGB values of the picked pixels',
        subtype='COLOR_GAMMA')),
    ('picker_mean', bpy.props.FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=4,
        description='The mean RGB values of the picked pixels',
        subtype='COLOR_GAMMA')),
    ('custom_size', bpy.props.IntProperty(
        default=10,
        min=2,
        soft_max=100,
        soft_min=5,
        name='Custom Tile Size',
        description='Custom tile size for color picker')),
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

# Register and unregister functions
def register():
    window_manager = bpy.types.WindowManager
    for name, prop in window_manager_props:
        setattr(window_manager, name, prop)
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()

def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    for name, _ in window_manager_props:
        delattr(bpy.types.WindowManager, name)

if __name__ == '__main__':
    register()
