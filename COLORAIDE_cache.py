"""
Python-side color caching for performance optimization.
Avoids Blender property system overhead during slider drag.

This module provides a caching layer that stores color updates in pure Python
before flushing them to Blender properties. This significantly improves performance
when updating many live-synced properties.
"""

import bpy

# Global cache for pending color updates (avoids Blender property overhead)
_COLOR_CACHE = {}  # {cache_key: (color, color_space)}
_FLUSH_SCHEDULED = False


def cache_color_update(obj_name, prop_path, color, color_space):
    """
    Store color in Python cache instead of immediately updating Blender property.
    This is FAST (~0.001ms) compared to Blender property updates (~10ms).
    
    Args:
        obj_name: Name of the object
        prop_path: Property path string
        color: (r, g, b) tuple in scene linear space
        color_space: 'LINEAR' or 'COLOR_GAMMA'
    """
    cache_key = f"{obj_name}:{prop_path}"
    _COLOR_CACHE[cache_key] = (tuple(color[:3]), color_space)


def flush_color_cache(context):
    """
    Flush all cached colors to actual Blender properties.
    This is the SLOW part, but happens less frequently.
    
    Args:
        context: Blender context
    
    Returns:
        None (for timer compatibility)
    """
    global _COLOR_CACHE, _FLUSH_SCHEDULED
    
    if not _COLOR_CACHE:
        _FLUSH_SCHEDULED = False
        return None  # Nothing to flush
    
    from .COLORAIDE_object_colors import set_color_value
    from .COLORAIDE_sync import live_sync_lock
    
    # Use live sync lock to prevent recursion during flush
    with live_sync_lock() as acquired:
        if not acquired:
            # Already flushing, reschedule
            _FLUSH_SCHEDULED = False
            return 0.05  # Try again in 50ms
        
        # Track which objects were modified
        updated_objects = set()
        
        # Write all cached colors to Blender
        for cache_key, (color, color_space) in _COLOR_CACHE.items():
            try:
                obj_name, prop_path = cache_key.split(':', 1)
                obj = bpy.data.objects.get(obj_name)
                
                if obj:
                    set_color_value(obj, prop_path, color, color_space)
                    updated_objects.add(obj)
            except Exception as e:
                print(f"Error flushing color cache for {cache_key}: {e}")
        
        # Single depsgraph update for all modified objects
        for obj in updated_objects:
            try:
                obj.update_tag()
            except:
                pass
        
        # Single view layer update
        if updated_objects and context.view_layer:
            try:
                context.view_layer.update()
            except:
                pass
        
        # Clear cache
        _COLOR_CACHE.clear()
        _FLUSH_SCHEDULED = False
        
        return None  # For timer


def schedule_flush(context, mode='BATCHED_TIMER'):
    """
    Schedule a flush based on update mode.
    
    Args:
        context: Blender context
        mode: 'IMMEDIATE', 'BATCHED_TIMER', or 'ON_RELEASE'
    """
    global _FLUSH_SCHEDULED
    
    if mode == 'IMMEDIATE':
        # Flush right now
        flush_color_cache(context)
    
    elif mode == 'BATCHED_TIMER':
        # Flush after 100ms (if not already scheduled)
        if not _FLUSH_SCHEDULED:
            _FLUSH_SCHEDULED = True
            bpy.app.timers.register(lambda: flush_color_cache(context), first_interval=0.1)
    
    elif mode == 'ON_RELEASE':
        # Don't flush - will happen when user releases mouse
        # This is handled by a separate system that detects mouse release
        pass


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
    """Clear all cached colors (useful for cleanup)"""
    global _COLOR_CACHE, _FLUSH_SCHEDULED
    _COLOR_CACHE.clear()
    _FLUSH_SCHEDULED = False


__all__ = [
    'cache_color_update',
    'flush_color_cache',
    'schedule_flush',
    'update_live_synced_properties_cached',
    'clear_cache'
]