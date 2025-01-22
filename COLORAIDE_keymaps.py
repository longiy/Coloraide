"""
Keymap management system for Coloraide addon.
Handles registration and cleanup of addon hotkeys.
"""

import bpy

# Storage for keymap items to enable proper cleanup
addon_keymaps = []

def register_keymaps():
    """Register all addon keymaps"""
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        # 3D View keymap
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        
        # Quick pick in 3D View
        kmi = km.keymap_items.new(
            "image.quickpick",
            "BACK_SLASH",
            "PRESS"
        )
        addon_keymaps.append((km, kmi))
        
        # Screen picker in 3D View (optional)
        kmi = km.keymap_items.new(
            "image.screen_picker",
            "C",
            "PRESS",
            alt=True
        )
        addon_keymaps.append((km, kmi))
        
        # Image Editor keymap
        km = kc.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
        
        # Quick pick in Image Editor
        kmi = km.keymap_items.new(
            "image.quickpick",
            "BACK_SLASH",
            "PRESS"
        )
        addon_keymaps.append((km, kmi))
        
        # Screen picker in Image Editor (optional)
        kmi = km.keymap_items.new(
            "image.screen_picker",
            "C",
            "PRESS",
            alt=True
        )
        addon_keymaps.append((km, kmi))
        
        # Clip Editor keymap
        km = kc.keymaps.new(name='Clip', space_type='CLIP_EDITOR')
        
        # Quick pick in Clip Editor
        kmi = km.keymap_items.new(
            "image.quickpick",
            "BACK_SLASH",
            "PRESS"
        )
        addon_keymaps.append((km, kmi))
        
        # Screen picker in Clip Editor (optional)
        kmi = km.keymap_items.new(
            "image.screen_picker",
            "C",
            "PRESS",
            alt=True
        )
        addon_keymaps.append((km, kmi))
        
        # Additional feature hotkeys
        
        # Normal sampler toggle
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            "brush.sample_normal",
            "N",
            "PRESS",
            alt=True
        )
        addon_keymaps.append((km, kmi))

def unregister_keymaps():
    """Unregister and remove all addon keymaps"""
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def get_hotkey_entry_item(km, kmi_name, kmi_value):
    """Utility function for finding keymap items"""
    for i, km_item in enumerate(km.keymap_items):
        if km_item.idname == kmi_name and km_item.name == kmi_value:
            return km_item
    return None