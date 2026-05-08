"""
Python-side color caching for performance optimization.
Avoids Blender property system overhead during slider drag.

This module provides a caching layer that stores color updates in pure Python
before flushing them to Blender properties. This significantly improves performance
when updating many live-synced properties.
"""

import bpy
from . import COLORAIDE_state as _state


def cache_color_update(obj_name, prop_path, color, color_space):
    """
    Store color in Python cache instead of immediately updating Blender property.
    This is FAST (~0.001ms) compared to Blender property updates (~10ms).
    """
    _state.color_cache[(obj_name, prop_path)] = (tuple(color[:3]), color_space)


def flush_color_cache(context):
    """
    Flush all cached colors to actual Blender properties.
    This is the SLOW part, but happens less frequently.

    Returns None (for timer compatibility).
    """
    if not _state.color_cache:
        _state.is_flush_scheduled = False
        return None

    from .COLORAIDE_object_colors import set_color_value
    from .COLORAIDE_sync import live_sync_lock

    with live_sync_lock() as acquired:
        if not acquired:
            _state.is_flush_scheduled = False
            return 0.05  # retry in 50ms

        updated_objects = set()

        for cache_key, (color, color_space) in _state.color_cache.items():
            try:
                obj_name, prop_path = cache_key
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    set_color_value(obj, prop_path, color, color_space)
                    updated_objects.add(obj)
            except Exception as e:
                print(f"Error flushing color cache for {cache_key}: {e}")

        for obj in updated_objects:
            try:
                obj.update_tag()
            except:
                pass

        if updated_objects and context.view_layer:
            try:
                context.view_layer.update()
            except:
                pass

        _state.color_cache.clear()
        _state.is_flush_scheduled = False
        return None


def schedule_flush(context, mode='BATCHED_TIMER'):
    """Schedule a cache flush based on the configured update mode."""
    if mode == 'IMMEDIATE':
        flush_color_cache(context)

    elif mode == 'BATCHED_TIMER':
        if not _state.is_flush_scheduled:
            _state.is_flush_scheduled = True
            bpy.app.timers.register(lambda: flush_color_cache(context), first_interval=0.1)

    # ON_RELEASE: no-op — flush triggered externally on mouse release


def update_live_synced_properties_cached(context, color, mode='absolute', delta=None):
    """
    Update live-synced properties using Python cache.
    This is the fast version that avoids Blender property overhead.
    
    Args:
        context: Blender context
        color: Target color in scene linear space
        mode: 'absolute' or 'relative'
        delta: Color delta for relative mode
    
    Returns:
        int: Number of properties updated
    """
    wm = context.window_manager
    obj_colors = wm.coloraide_object_colors
    
    # Get update mode from preferences
    try:
        # Get addon name from module path
        addon_name = __name__.split('.')[0]
        
        # Try to get addon preferences
        if addon_name in context.preferences.addons:
            addon_prefs = context.preferences.addons[addon_name].preferences
            if hasattr(addon_prefs, 'live_sync_mode'):
                update_mode = addon_prefs.live_sync_mode
            else:
                update_mode = 'IMMEDIATE'
        else:
            update_mode = 'IMMEDIATE'
    except Exception as e:
        print(f"Coloraide: Could not access preferences ({e}), using IMMEDIATE mode")
        update_mode = 'IMMEDIATE'
    
    updated_count = 0
    
    for item in obj_colors.items:
        if not item.live_sync:
            continue
        
        # Calculate final color
        if mode == 'relative' and delta:
            current = tuple(item.color[:3])
            final_color = tuple(max(0.0, min(1.0, c + d)) for c, d in zip(current, delta))
        else:
            final_color = color
        
        # Update UI swatch immediately (so user sees change)
        item.suppress_updates = True
        item.color = final_color
        item.suppress_updates = False
        
        # Cache the update instead of applying immediately
        if item.property_path == '__GROUP__':
            # Handle grouped items
            parts = item.object_name.split('|')
            instances = parts[2:] if len(parts) > 2 else []
            
            for inst_str in instances:
                try:
                    obj_name, prop_path, color_space = inst_str.split(':')
                    cache_color_update(obj_name, prop_path, final_color, color_space)
                    updated_count += 1
                except:
                    pass
        else:
            # Handle individual items
            cache_color_update(item.object_name, item.property_path, final_color, item.color_space)
            updated_count += 1
    
    # Schedule flush based on mode
    if updated_count > 0:
        schedule_flush(context, update_mode)
    
    return updated_count


def clear_cache():
    """Clear all cached colors."""
    _state.color_cache.clear()
    _state.is_flush_scheduled = False


__all__ = [
    'cache_color_update',
    'flush_color_cache',
    'schedule_flush',
    'update_live_synced_properties_cached',
    'clear_cache'
]