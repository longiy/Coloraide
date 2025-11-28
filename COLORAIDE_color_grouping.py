"""
Color grouping utilities for Figma-style grouped color mode.
Groups identical colors with tolerance-based matching.
"""

import bpy
from .COLORAIDE_colorspace import linear_to_hex


def colors_match(color1, color2, tolerance=0.001):
    """
    Check if two colors match within tolerance.
    
    Args:
        color1: (r, g, b) tuple in scene linear space
        color2: (r, g, b) tuple in scene linear space
        tolerance: Maximum difference per channel to consider match
    
    Returns:
        bool: True if colors match within tolerance
    """
    if len(color1) < 3 or len(color2) < 3:
        return False
    
    return all(abs(a - b) < tolerance for a, b in zip(color1[:3], color2[:3]))


def find_color_group_index(color, existing_groups, tolerance):
    """
    Find which existing group a color belongs to.
    
    Args:
        color: (r, g, b) tuple to match
        existing_groups: List of color group items
        tolerance: Matching tolerance
    
    Returns:
        int: Index of matching group, or -1 if no match
    """
    for i, group in enumerate(existing_groups):
        if colors_match(color, group.color[:3], tolerance):
            return i
    return -1


def group_colors_by_value(detected_colors, tolerance=0.001):
    """
    Group color properties by similar color values.
    
    Args:
        detected_colors: List of color property dicts from scan functions
        tolerance: Color matching tolerance
    
    Returns:
        List of dicts with structure:
        {
            'color': (r, g, b),
            'hex': '#RRGGBB',
            'count': int,
            'instances': [list of property dicts]
        }
    """
    groups = []
    
    for color_data in detected_colors:
        color = tuple(color_data['color'][:3])
        
        # Find existing group or create new one
        group_idx = -1
        for i, group in enumerate(groups):
            if colors_match(color, group['color'], tolerance):
                group_idx = i
                break
        
        if group_idx >= 0:
            # Add to existing group
            groups[group_idx]['instances'].append(color_data)
            groups[group_idx]['count'] += 1
        else:
            # Create new group
            groups.append({
                'color': color,
                'hex': linear_to_hex(color),
                'count': 1,
                'instances': [color_data]
            })
    
    # Sort by usage count (most used first)
    groups.sort(key=lambda g: g['count'], reverse=True)
    
    return groups


def build_grouped_properties(context, detected_colors, tolerance):
    """
    Build grouped color properties from detected colors.
    
    Args:
        context: Blender context
        detected_colors: List of color property dicts
        tolerance: Color matching tolerance
    
    Returns:
        None (updates context.window_manager.coloraide_object_colors directly)
    """
    wm = context.window_manager
    obj_colors = wm.coloraide_object_colors
    
    # Group colors
    groups_data = group_colors_by_value(detected_colors, tolerance)
    
    # Clear existing grouped properties (if we add them later)
    # For now we'll just use the object mode items
    
    print(f"\n{'='*60}")
    print(f"COLOR GROUPING RESULTS")
    print(f"{'='*60}")
    print(f"Total properties: {len(detected_colors)}")
    print(f"Unique colors: {len(groups_data)}")
    print(f"Tolerance: {tolerance:.4f}")
    
    for i, group in enumerate(groups_data):
        print(f"\nGroup {i+1}: {group['hex']} (used {group['count']}×)")
        for instance in group['instances']:
            print(f"  • {instance['label_short']}")
    
    print(f"{'='*60}\n")
    
    return groups_data


def update_all_instances_in_group(context, group_color, instance_list):
    """
    Update all color instances in a group to a new color value.
    
    Args:
        context: Blender context
        group_color: New color (r, g, b) in scene linear space
        instance_list: List of ColorPropertyInstance items
    
    Returns:
        tuple: (success_count, failed_count)
    """
    from .COLORAIDE_object_colors import set_color_value
    
    success_count = 0
    failed_count = 0
    
    for instance in instance_list:
        obj = bpy.data.objects.get(instance.object_name)
        if not obj:
            failed_count += 1
            continue
        
        if set_color_value(obj, instance.property_path, group_color, instance.color_space):
            success_count += 1
        else:
            failed_count += 1
    
    return success_count, failed_count


__all__ = [
    'colors_match',
    'find_color_group_index',
    'group_colors_by_value',
    'build_grouped_properties',
    'update_all_instances_in_group'
]
