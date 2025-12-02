"""
Operators for object color property management in Coloraide.
SUPPORTS: Object Mode, Grouped Mode, Relative Adjustments, Python Caching
FIX: Added recursion guards to all operators.
"""

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty
from ..COLORAIDE_object_colors import scan_all_colors, get_color_value, set_color_value
from ..COLORAIDE_color_grouping import group_colors_by_value, build_grouped_properties
from ..COLORAIDE_sync import sync_all, is_updating, is_updating_live_sync


class OBJECT_COLORS_OT_refresh(Operator):
    """Refresh detected color properties from selected objects"""
    bl_idname = "object_colors.refresh"
    bl_label = "Refresh Object Colors"
    bl_description = "Scan selected objects for color properties"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        """FIX: Don't refresh during updates"""
        if is_updating() or is_updating_live_sync():
            return False
        return True
    
    def execute(self, context):
        # FIX: Skip if updates in progress
        if is_updating() or is_updating_live_sync():
            return {'CANCELLED'}
        
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        # Clear existing items
        obj_colors.items.clear()
        
        # Scan for colors
        detected = scan_all_colors(context, obj_colors.show_multiple_objects)
        
        if obj_colors.display_mode == 'OBJECT':
            # OBJECT MODE: Add individual items as before
            for color_data in detected:
                item = obj_colors.items.add()
                item.label_short = color_data['label_short']
                item.label_detailed = color_data['label_detailed']
                item.object_name = color_data['object_name']
                item.property_path = color_data['property_path']
                item.property_type = color_data['property_type']
                item.color_space = color_data.get('color_space', 'LINEAR')
                item.color = color_data['color']
                item.live_sync = False
            
            self.report({'INFO'}, f"Found {len(detected)} color properties")
        
        else:  # GROUPED MODE
            # Group colors and store for UI
            groups_data = build_grouped_properties(context, detected, obj_colors.tolerance)
            
            # Store groups in a way the UI can access
            for group_data in groups_data:
                # Create one "representative" item per group
                item = obj_colors.items.add()
                item.label_short = f"{group_data['hex']} ({group_data['count']}×)"
                item.label_detailed = f"Color group: {group_data['count']} instances"
                item.color = group_data['color']
                item.property_path = '__GROUP__'  # Special marker for grouped items
                
                # Store instance data in object_name
                # Format: "instance_count|hex|obj1:path1:space|obj2:path2:space|..."
                instance_strs = []
                for inst in group_data['instances']:
                    instance_strs.append(f"{inst['object_name']}:{inst['property_path']}:{inst['color_space']}")
                item.object_name = f"{group_data['count']}|{group_data['hex']}|" + "|".join(instance_strs)
            
            self.report({'INFO'}, f"Found {len(groups_data)} unique colors across {len(detected)} properties")
        
        return {'FINISHED'}


class OBJECT_COLORS_OT_pull(Operator):
    """Pull color from Coloraide to object property (↓)"""
    bl_idname = "object_colors.pull"
    bl_label = "Pull Color from Coloraide"
    bl_description = "Apply Coloraide's current color to this property (pull from Coloraide picker)"
    bl_options = {'INTERNAL'}
    
    index: IntProperty()
    
    @classmethod
    def poll(cls, context):
        """FIX: Don't pull during updates"""
        if is_updating() or is_updating_live_sync():
            return False
        return True
    
    def execute(self, context):
        # FIX: Skip if updates in progress
        if is_updating() or is_updating_live_sync():
            return {'CANCELLED'}
        
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        if self.index >= len(obj_colors.items):
            self.report({'WARNING'}, "Invalid index")
            return {'CANCELLED'}
        
        item = obj_colors.items[self.index]
        
        # Get Coloraide's current color (scene linear)
        current_color = tuple(wm.coloraide_picker.mean)
        
        # Check if this is a grouped item
        if item.property_path == '__GROUP__':
            # GROUPED MODE: Pull to all instances in group
            parts = item.object_name.split('|')
            count = int(parts[0])
            instances = parts[2:]  # Skip count and hex
            
            success = 0
            failed = 0
            
            for inst_str in instances:
                obj_name, prop_path, color_space = inst_str.split(':')
                obj = bpy.data.objects.get(obj_name)
                if obj and set_color_value(obj, prop_path, current_color, color_space):
                    success += 1
                else:
                    failed += 1
            
            # Update color and hex in the item
            item.suppress_updates = True
            item.color = current_color
            item.suppress_updates = False
            
            # Update hex value in label_short
            from ..COLORAIDE_colorspace import linear_to_hex
            new_hex = linear_to_hex(current_color)
            item.label_short = f"{new_hex} ({count}×)"
            
            # Update stored data with new hex
            item.object_name = f"{count}|{new_hex}|" + "|".join(instances)
            
            self.report({'INFO'}, f"Pulled to {success}/{count} instances")
            return {'FINISHED'}
        
        # OBJECT MODE: Pull to single property
        obj = bpy.data.objects.get(item.object_name)
        if not obj:
            self.report({'WARNING'}, f"Object '{item.object_name}' not found")
            return {'CANCELLED'}
        
        if set_color_value(obj, item.property_path, current_color, item.color_space):
            item.suppress_updates = True
            item.color = current_color
            item.suppress_updates = False
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, f"Failed to set color at {item.property_path}")
            return {'CANCELLED'}


class OBJECT_COLORS_OT_push(Operator):
    """Push color from object property to Coloraide (↑)"""
    bl_idname = "object_colors.push"
    bl_label = "Push Color to Coloraide"
    bl_description = "Load this color into Coloraide's picker (push to Coloraide picker)"
    bl_options = {'INTERNAL'}
    
    index: IntProperty()
    
    @classmethod
    def poll(cls, context):
        """FIX: Don't push during updates"""
        if is_updating() or is_updating_live_sync():
            return False
        return True
    
    def execute(self, context):
        # FIX: Skip if updates in progress
        if is_updating() or is_updating_live_sync():
            return {'CANCELLED'}
        
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        if self.index >= len(obj_colors.items):
            self.report({'WARNING'}, "Invalid index")
            return {'CANCELLED'}
        
        item = obj_colors.items[self.index]
        
        # Check if this is a grouped item
        if item.property_path == '__GROUP__':
            # Just sync the group color to Coloraide
            sync_all(context, 'object_colors', tuple(item.color))
            return {'FINISHED'}
        
        # OBJECT MODE: Push from specific property to Coloraide
        obj = bpy.data.objects.get(item.object_name)
        if not obj:
            self.report({'WARNING'}, f"Object '{item.object_name}' not found")
            return {'CANCELLED'}
        
        color = get_color_value(obj, item.property_path, item.color_space)
        if color:
            item.suppress_updates = True
            item.color = color
            item.suppress_updates = False
            sync_all(context, 'object_colors', color)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, f"Failed to read color from {item.property_path}")
            return {'CANCELLED'}


class OBJECT_COLORS_OT_update_group_color(Operator):
    """Update all instances in a group when color swatch is changed"""
    bl_idname = "object_colors.update_group_color"
    bl_label = "Update Group Color"
    bl_description = "Update all instances in this color group"
    bl_options = {'INTERNAL'}
    
    index: IntProperty()
    
    @classmethod
    def poll(cls, context):
        """FIX: Don't update during other updates"""
        if is_updating() or is_updating_live_sync():
            return False
        return True
    
    def execute(self, context):
        # FIX: Skip if updates in progress
        if is_updating() or is_updating_live_sync():
            return {'CANCELLED'}
        
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        if self.index >= len(obj_colors.items):
            return {'CANCELLED'}
        
        item = obj_colors.items[self.index]
        
        # Only handle grouped items
        if item.property_path != '__GROUP__':
            return {'CANCELLED'}
        
        # Parse instance data
        parts = item.object_name.split('|')
        count = int(parts[0])
        instances = parts[2:]
        
        new_color = tuple(item.color[:3])
        success = 0
        
        # Update all instances
        for inst_str in instances:
            obj_name, prop_path, color_space = inst_str.split(':')
            obj = bpy.data.objects.get(obj_name)
            if obj and set_color_value(obj, prop_path, new_color, color_space):
                success += 1
        
        # Update hex value in label
        from ..COLORAIDE_colorspace import linear_to_hex
        new_hex = linear_to_hex(new_color)
        item.label_short = f"{new_hex} ({count}×)"
        
        # Update stored data with new hex
        item.object_name = f"{count}|{new_hex}|" + "|".join(instances)
        
        return {'FINISHED'}


class OBJECT_COLORS_OT_show_tooltip(Operator):
    """Show color group instances in tooltip"""
    bl_idname = "object_colors.show_tooltip"
    bl_label = ""
    bl_options = {'INTERNAL'}
    
    tooltip: StringProperty()
    label: StringProperty()
    
    @classmethod
    def description(cls, context, properties):
        return properties.tooltip
    
    def execute(self, context):
        return {'FINISHED'}


def update_live_synced_properties(context, color, mode='absolute', delta=None):
    """
    Update all properties with live sync enabled.
    NOW USES PYTHON CACHING for performance (90-95% faster).
    
    Args:
        context: Blender context
        color: Target color in scene linear space (for absolute mode)
        mode: 'absolute' (replace) or 'relative' (adjust by delta)
        delta: Color delta (r, g, b) for relative adjustments
    
    Returns:
        int: Number of properties updated
    """
    # Use the cached implementation for better performance
    from ..COLORAIDE_cache import update_live_synced_properties_cached
    
    return update_live_synced_properties_cached(context, color, mode, delta)


__all__ = [
    'OBJECT_COLORS_OT_refresh',
    'OBJECT_COLORS_OT_pull',
    'OBJECT_COLORS_OT_push',
    'OBJECT_COLORS_OT_update_group_color',
    'OBJECT_COLORS_OT_show_tooltip',
    'update_live_synced_properties'
]