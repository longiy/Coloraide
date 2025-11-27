"""
Object color property detection and access for Coloraide.
Scans objects for color properties and provides get/set functionality.

Color Space Notes:
- GeoNodes color inputs: Scene linear
- Material node COLOR sockets: Scene linear  
- Light.color: Scene linear
- Object.color: sRGB (viewport display)
"""

import bpy
from mathutils import Color
from .COLORAIDE_colorspace import rgb_srgb_to_linear, rgb_linear_to_srgb


def is_node_connected_to_output(node, node_tree):
    """Check if node contributes to the final output (traces back to Material Output)"""
    if not node_tree:
        return False
    
    # Find active Material Output node
    output_node = None
    for n in node_tree.nodes:
        if n.type == 'OUTPUT_MATERIAL' and n.is_active_output:
            output_node = n
            break
    
    if not output_node:
        return False
    
    # BFS to check if node connects to output
    visited = set()
    to_check = [output_node]
    
    while to_check:
        current = to_check.pop(0)
        if current in visited:
            continue
        visited.add(current)
        
        if current == node:
            return True
        
        # Check all input sockets
        for input_socket in current.inputs:
            if input_socket.is_linked:
                for link in input_socket.links:
                    to_check.append(link.from_node)
    
    return False


def scan_geonodes_colors(obj):
    """Scan GeometryNodes modifiers for color inputs (scene linear)"""
    colors = []
    
    for mod in obj.modifiers:
        if mod.type != 'NODES' or not mod.node_group:
            continue
        
        # Access inputs through the interface (Blender 4.0+ API)
        node_group = mod.node_group
        if not hasattr(node_group, 'interface'):
            continue
        
        # Iterate through interface items
        for item in node_group.interface.items_tree:
            # Check if it's an input socket of color type
            if not hasattr(item, 'item_type') or item.item_type != 'SOCKET':
                continue
            
            if not hasattr(item, 'in_out') or item.in_out != 'INPUT':
                continue
            
            # Check for color socket types
            if not hasattr(item, 'socket_type'):
                continue
            
            if item.socket_type != 'NodeSocketColor':
                continue
            
            # Get the identifier for accessing the modifier property
            identifier = item.identifier
            
            # Get current value from modifier
            try:
                # Try to get value from modifier dictionary-like access
                if identifier in mod:
                    value = mod[identifier]
                    if hasattr(value, '__len__') and len(value) >= 3:
                        # GeoNodes colors are already scene linear - store as-is
                        colors.append({
                            'label_short': f"GN:{item.name}",
                            'label_detailed': f"Geometry Nodes > {mod.name} > {item.name}",
                            'object_name': obj.name,
                            'property_path': f'modifiers["{mod.name}"]["{identifier}"]',
                            'property_type': 'GEONODES',
                            'color': tuple(value[:3]),  # Already linear
                            'color_space': 'LINEAR'
                        })
            except Exception as e:
                # Silently skip if we can't access this input
                pass
    
    return colors


def scan_material_colors(obj):
    """Scan materials for color properties (only connected nodes, scene linear)"""
    colors = []
    
    if not hasattr(obj, 'material_slots'):
        return colors
    
    for slot_idx, slot in enumerate(obj.material_slots):
        mat = slot.material
        if not mat or not mat.node_tree:
            continue
        
        mat_label = mat.name[:10] + "..." if len(mat.name) > 10 else mat.name
        
        # Scan nodes
        for node in mat.node_tree.nodes:
            # Skip if node doesn't connect to output
            if not is_node_connected_to_output(node, mat.node_tree):
                continue
            
            # Check Principled BSDF special cases
            if node.type == 'BSDF_PRINCIPLED':
                # Base Color
                if 'Base Color' in node.inputs:
                    socket = node.inputs['Base Color']
                    if not socket.is_linked:
                        # Material node colors are already scene linear
                        colors.append({
                            'label_short': f"{mat_label}:Base",
                            'label_detailed': f"Material '{mat.name}' > {node.name} > Base Color",
                            'object_name': obj.name,
                            'property_path': f'material_slots[{slot_idx}].material.node_tree.nodes["{node.name}"].inputs["Base Color"].default_value',
                            'property_type': 'MATERIAL',
                            'color': tuple(socket.default_value[:3]),  # Already linear
                            'color_space': 'LINEAR'
                        })
                
                # Emission (only if Emission Strength > 0.001)
                if 'Emission Color' in node.inputs and 'Emission Strength' in node.inputs:
                    emission_strength = node.inputs['Emission Strength'].default_value
                    if emission_strength > 0.001:
                        socket = node.inputs['Emission Color']
                        if not socket.is_linked:
                            colors.append({
                                'label_short': f"{mat_label}:Emission",
                                'label_detailed': f"Material '{mat.name}' > {node.name} > Emission Color",
                                'object_name': obj.name,
                                'property_path': f'material_slots[{slot_idx}].material.node_tree.nodes["{node.name}"].inputs["Emission Color"].default_value',
                                'property_type': 'MATERIAL',
                                'color': tuple(socket.default_value[:3]),  # Already linear
                                'color_space': 'LINEAR'
                            })
            
            # RGB Node
            elif node.type == 'RGB':
                colors.append({
                    'label_short': f"{mat_label}:{node.name}",
                    'label_detailed': f"Material '{mat.name}' > RGB Node '{node.name}'",
                    'object_name': obj.name,
                    'property_path': f'material_slots[{slot_idx}].material.node_tree.nodes["{node.name}"].outputs[0].default_value',
                    'property_type': 'MATERIAL',
                    'color': tuple(node.outputs[0].default_value[:3]),  # Already linear
                    'color_space': 'LINEAR'
                })
            
            # Mix/Combine Color nodes - check color inputs
            elif node.type in {'MIX', 'MIX_RGB', 'COMBCOLOR_RGB', 'COMBCOLOR_HSV', 'COMBCOLOR_HSL'}:
                for input_socket in node.inputs:
                    if input_socket.type == 'RGBA' and not input_socket.is_linked:
                        socket_name_short = input_socket.name[:6]
                        colors.append({
                            'label_short': f"{mat_label}:{node.name[:6]}:{socket_name_short}",
                            'label_detailed': f"Material '{mat.name}' > {node.name} > {input_socket.name}",
                            'object_name': obj.name,
                            'property_path': f'material_slots[{slot_idx}].material.node_tree.nodes["{node.name}"].inputs["{input_socket.name}"].default_value',
                            'property_type': 'MATERIAL',
                            'color': tuple(input_socket.default_value[:3]),  # Already linear
                            'color_space': 'LINEAR'
                        })
    
    return colors


def scan_light_colors(obj):
    """Scan light object for color property (scene linear)"""
    colors = []
    
    if obj.type == 'LIGHT' and obj.data:
        # Light colors are already scene linear
        colors.append({
            'label_short': "Light:Color",
            'label_detailed': f"Light '{obj.name}' > Color",
            'object_name': obj.name,
            'property_path': 'data.color',
            'property_type': 'LIGHT',
            'color': tuple(obj.data.color[:3]),  # Already linear
            'color_space': 'LINEAR'
        })
    
    return colors


def scan_object_colors(obj):
    """Scan object for viewport display color (sRGB -> convert to linear)"""
    colors = []
    
    # Object viewport color is sRGB - convert to linear for storage
    obj_color_srgb = tuple(obj.color[:3])
    obj_color_linear = rgb_srgb_to_linear(obj_color_srgb)
    
    colors.append({
        'label_short': "Obj:Color",
        'label_detailed': f"Object '{obj.name}' > Viewport Display Color",
        'object_name': obj.name,
        'property_path': 'color',
        'property_type': 'OBJECT',
        'color': obj_color_linear,  # Converted to linear
        'color_space': 'SRGB'  # Mark as sRGB so we convert back when writing
    })
    
    return colors


def scan_greasepencil_colors(obj):
    """Scan Grease Pencil materials for fill and stroke colors (sRGB -> convert to linear)"""
    colors = []
    
    # Check for both old GPENCIL and new GREASEPENCIL types (Blender 4.3+)
    if obj.type not in {'GPENCIL', 'GREASEPENCIL'}:
        return colors
    
    # Check if object has data and materials
    if not hasattr(obj, 'data') or not obj.data:
        return colors
    
    if not hasattr(obj.data, 'materials'):
        return colors
    
    # Scan through all material slots
    for mat_idx, mat in enumerate(obj.data.materials):
        if not mat:
            continue
        
        # Try old GP system (pre-4.3)
        if hasattr(mat, 'grease_pencil'):
            gp_settings = mat.grease_pencil
            mat_label = mat.name[:10] + "..." if len(mat.name) > 10 else mat.name
            
            # Fill color - convert sRGB to linear
            if hasattr(gp_settings, 'fill_color'):
                fill_linear = tuple(gp_settings.fill_color[:3])
                
                colors.append({
                    'label_short': f"GP:{mat_label}:Fill",
                    'label_detailed': f"Grease Pencil Material '{mat.name}' > Fill Color",
                    'object_name': obj.name,
                    'property_path': f'data.materials[{mat_idx}].grease_pencil.fill_color',
                    'property_type': 'GPENCIL',
                    'color': fill_linear,  # Converted to linear
                    'color_space': 'SRGB'  # Mark as sRGB so we convert back when writing
                })
            
            # Stroke color - convert sRGB to linear
            if hasattr(gp_settings, 'color'):
                stroke_srgb = tuple(gp_settings.color[:3])
                stroke_linear = rgb_srgb_to_linear(stroke_srgb)
                
                colors.append({
                    'label_short': f"GP:{mat_label}:Stroke",
                    'label_detailed': f"Grease Pencil Material '{mat.name}' > Stroke Color",
                    'object_name': obj.name,
                    'property_path': f'data.materials[{mat_idx}].grease_pencil.color',
                    'property_type': 'GPENCIL',
                    'color': stroke_linear,  # Converted to linear
                    'color_space': 'LINEAR'  # ← Change from 'SRGB' to 'LINEAR'
                })
        
        # Try new GP system (4.3+) - might use regular materials
        # In new GP, materials might just be regular materials with nodes
        # These will be caught by the regular material scanner
    
    return colors


def scan_all_colors(context, show_multiple=False):
    """Scan selected objects for all color properties"""
    all_colors = []
    
    if show_multiple:
        objects = list(context.selected_objects)
    else:
        objects = [context.active_object] if context.active_object else []
    
    for obj in objects:
        if not obj:
            continue
        
        # Scan different property types
        all_colors.extend(scan_geonodes_colors(obj))
        all_colors.extend(scan_material_colors(obj))
        all_colors.extend(scan_light_colors(obj))
        all_colors.extend(scan_greasepencil_colors(obj))
        all_colors.extend(scan_object_colors(obj))
    
    return all_colors


def get_color_value(obj, property_path, color_space='LINEAR'):
    """
    Get color value from object using property path.
    Returns color in scene linear space regardless of source color space.
    
    Args:
        obj: Blender object
        property_path: Path to color property
        color_space: 'LINEAR' or 'SRGB' - the space the property is stored in
    
    Returns:
        tuple: (r, g, b) in scene linear space, or None
    """
    try:
        # Special handling for modifier dictionary access (GeoNodes)
        if 'modifiers[' in property_path and '"][' in property_path:
            # Extract modifier name and key: modifiers["Name"]["key"]
            parts = property_path.split('"]["')
            mod_part = parts[0].replace('modifiers["', '')
            key = parts[1].replace('"]', '')
            
            mod = obj.modifiers.get(mod_part)
            if mod and key in mod:
                value = mod[key]
                if hasattr(value, '__len__') and len(value) >= 3:
                    color = tuple(value[:3])
                    # Convert to linear if needed
                    if color_space == 'SRGB':
                        color = rgb_srgb_to_linear(color)
                    return color
            return None
        
        # Standard property access
        value = eval(f"obj.{property_path}")
        if hasattr(value, '__len__') and len(value) >= 3:
            color = tuple(value[:3])
            # Convert to linear if needed
            if color_space == 'SRGB':
                color = rgb_srgb_to_linear(color)
            return color
        return None
    except Exception as e:
        print(f"Error getting color from {property_path}: {e}")
        return None


def set_color_value(obj, property_path, color, color_space='LINEAR'):
    """
    Set color value on object using property path.
    
    Args:
        obj: Blender object
        property_path: Path to color property
        color: (r, g, b) tuple in scene linear space
        color_space: 'LINEAR' or 'SRGB' - the space the property should be stored in
    
    Returns:
        bool: True if successful
    """
    try:
        # Convert from linear if needed
        if color_space == 'SRGB':
            color = rgb_linear_to_srgb(color)
        
        # Special handling for modifier dictionary access (GeoNodes)
        if 'modifiers[' in property_path and '"][' in property_path:
            # Extract modifier name and key: modifiers["Name"]["key"]
            parts = property_path.split('"]["')
            mod_part = parts[0].replace('modifiers["', '')
            key = parts[1].replace('"]', '')
            
            mod = obj.modifiers.get(mod_part)
            if mod and key in mod:
                # Get current value to preserve alpha if present
                current = mod[key]
                if hasattr(current, '__len__'):
                    if len(current) == 3:
                        mod[key] = color
                    elif len(current) == 4:
                        mod[key] = tuple(color) + (current[3],)
                else:
                    mod[key] = color
                
                # CRITICAL: Force depsgraph update for GeoNodes
                obj.update_tag()
                if bpy.context.view_layer:
                    bpy.context.view_layer.update()
                
                return True
            return False
        
        # Standard property path - split into container and attribute
        if '.' in property_path:
            path_parts = property_path.rsplit('.', 1)
            container_path = path_parts[0]
            attr = path_parts[1]
            
            # Evaluate container
            container = eval(f"obj.{container_path}")
            current = getattr(container, attr)
            
            # Handle different color types
            if hasattr(current, '__len__'):
                if len(current) == 3:
                    setattr(container, attr, color)
                elif len(current) == 4:
                    # Preserve alpha channel
                    setattr(container, attr, tuple(color) + (current[3],))
            else:
                setattr(container, attr, color)
            
            # Trigger update for materials/lights
            obj.update_tag()
            if bpy.context.view_layer:
                bpy.context.view_layer.update()
            
            return True
        else:
            # Direct attribute on object
            current = getattr(obj, property_path)
            if hasattr(current, '__len__'):
                if len(current) == 3:
                    setattr(obj, property_path, color)
                elif len(current) == 4:
                    setattr(obj, property_path, tuple(color) + (current[3],))
            else:
                setattr(obj, property_path, color)
            
            # Trigger viewport update
            obj.update_tag()
            if bpy.context.view_layer:
                bpy.context.view_layer.update()
            
            return True
            
    except Exception as e:
        print(f"Error setting color at {property_path}: {e}")
        import traceback
        traceback.print_exc()
        return False


__all__ = [
    'scan_all_colors',
    'get_color_value', 
    'set_color_value'
]