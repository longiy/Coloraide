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
    # Texture Paint keymap
        km = kc.keymaps.new(name='Image Paint', space_type='VIEW_3D', region_type='WINDOW')
        kmi = km.keymap_items.new(
            "image.quickpick",
            "E",  # Changed from S
            "PRESS",
            shift=True  # Added shift modifier
        )
        addon_keymaps.append((km, kmi))
        
        # Regular 3D View keymap
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            "image.quickpick",
            "E",  # Changed from BACK_SLASH
            "PRESS",
            shift=True  # Added shift modifier
        )
        addon_keymaps.append((km, kmi))

        # Image Editor keymap
        km = kc.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
        kmi = km.keymap_items.new(
            "image.quickpick",
            "E",  # Changed from S
            "PRESS",
            shift=True  # Added shift modifier
        )
        addon_keymaps.append((km, kmi))

        # Clip Editor keymap
        km = kc.keymaps.new(name='Clip', space_type='CLIP_EDITOR')
        kmi = km.keymap_items.new(
            "image.quickpick",
            "E",  # Changed from BACK_SLASH
            "PRESS",
            shift=True  # Added shift modifier
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