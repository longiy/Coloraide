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
    
    if not kc:
        return
        
    # Check Blender version
    version = bpy.app.version
    is_blender_43_plus = (version[0] > 4) or (version[0] == 4 and version[1] >= 3)
    
    # For Blender 4.3+, we can use more specific keymaps
    if is_blender_43_plus:
        # Texture Paint keymap (4.3+ style)
        try:
            km = kc.keymaps.new(name='Image Paint', space_type='VIEW_3D', region_type='WINDOW')
            kmi = km.keymap_items.new(
                "image.quickpick",
                "E",
                "PRESS",
                shift=True
            )
            addon_keymaps.append((km, kmi))
        except Exception as e:
            print(f"Warning: Could not register Image Paint keymap for VIEW_3D: {e}")
        
        # Image Editor paint keymap (4.3+ style)
        try:
            km = kc.keymaps.new(name='Image Paint', space_type='IMAGE_EDITOR', region_type='WINDOW')
            kmi = km.keymap_items.new(
                "image.quickpick",
                "E",
                "PRESS",
                shift=True
            )
            addon_keymaps.append((km, kmi))
        except Exception as e:
            print(f"Warning: Could not register Image Paint keymap for IMAGE_EDITOR: {e}")
    
    # These keymaps work in all versions - fallback approach
    # Regular 3D View keymap
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(
        "image.quickpick",
        "E",
        "PRESS",
        shift=True
    )
    addon_keymaps.append((km, kmi))

    # Image Editor keymap
    km = kc.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
    kmi = km.keymap_items.new(
        "image.quickpick",
        "E",
        "PRESS",
        shift=True
    )
    addon_keymaps.append((km, kmi))

    # Clip Editor keymap
    km = kc.keymaps.new(name='Clip', space_type='CLIP_EDITOR')
    kmi = km.keymap_items.new(
        "image.quickpick",
        "E",
        "PRESS",
        shift=True
    )
    addon_keymaps.append((km, kmi))

def unregister_keymaps():
    """Unregister and remove all addon keymaps"""
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception as e:
            print(f"Warning: Could not remove keymap item: {e}")
    addon_keymaps.clear()

def get_hotkey_entry_item(km, kmi_name, kmi_value):
    """Utility function for finding keymap items"""
    for i, km_item in enumerate(km.keymap_items):
        if km_item.idname == kmi_name and km_item.name == kmi_value:
            return km_item
    return None