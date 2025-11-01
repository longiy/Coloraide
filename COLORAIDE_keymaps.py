"""
Keymap management system for Coloraide addon - Blender 5.0+
Simplified with version detection removed.
"""

import bpy

# Storage for keymap items to enable proper cleanup
addon_keymaps = []

def register_keymaps():
    """Register all addon keymaps for Blender 5.0+"""
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if not kc:
        return
    
    # Image Paint keymap for VIEW_3D
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
    
    # Image Paint keymap for IMAGE_EDITOR
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
    
    # Regular 3D View keymap (fallback)
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(
        "image.quickpick",
        "E",
        "PRESS",
        shift=True
    )
    addon_keymaps.append((km, kmi))

    # Image Editor keymap (fallback)
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
