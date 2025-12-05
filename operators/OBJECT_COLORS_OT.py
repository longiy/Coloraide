"""
Operators for object color property management in Coloraide.
CLEAN REWRITE: Simplified with auto-refresh on mode switch.
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
    bl_label = "Rescan Objects"
    bl_description = "Scan selected objects for color properties (preserves live sync toggles)"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        if is_updating() or is_updating_live_sync():
            return False
        return True
    
    def execute(self, context):
        if is_updating() or is_updating_live_sync():
            return {'CANCELLED'}
        
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        # Clear all caches for fresh scan
        from ..COLORAIDE_object_colors import clear_object_cache
        clear_object_cache()
        
        # Save live_sync states before clearing
        saved_live_sync = {}  # {(obj_name, prop_path): live_sync}
        
        for item in obj_colors.items:
            if item.property_path != '__GROUP__':
                # Individual item
                key = (item.object_name, item.property_path)
                saved_live_sync[key] = item.live_sync
            else:
                # Grouped item - save for all instances
                parts = item.object_name.split('|')
                instances = parts[2:] if len(parts) > 2 else []
                for inst_str in instances:
                    try:
                        obj_name, prop_path, _ = inst_str.split(':')
                        key = (obj_name, prop_path)
                        saved_live_sync[key] = item.live_sync
                    except:
                        pass
        
        # Scan objects
        detected = scan_all_colors(context, obj_colors.show_multiple_objects, use_cache=False)
        
        # Clear and rebuild based on mode
        obj_colors.items.clear()
        
        if obj_colors.display_mode == 'OBJECT':
            # OBJECT MODE: Individual items
            for data in detected:
                item = obj_colors.items.add()
                item.suppress_updates = True
                item.label_short = data['label_short']
                item.label_detailed = data['label_detailed']
                item.object_name = data['object_name']
                item.property_path = data['property_path']
                item.property_type = data['property_type']
                item.color_space = data.get('color_space', 'LINEAR')
                item.color = data['color']
                
                # Restore live_sync
                key = (data['object_name'], data['property_path'])
                item.live_sync = saved_live_sync.get(key, False)
                
                item.suppress_updates = False
            
            self.report({'INFO'}, f"Found {len(detected)} color properties")
        
        else:  # GROUPED MODE
            # Group colors
            groups_data = build_grouped_properties(context, detected, obj_colors.tolerance)
            
            for group_data in groups_data:
                item = obj_colors.items.add()
                item.suppress_updates = True
                item.label_short = f"{group_data['hex']} ({group_data['count']}×)"
                item.label_detailed = f"Color group: {group_data['count']} instances"
                item.property_path = '__GROUP__'
                item.color = group_data['color']
                
                # Build instance data string
                instance_strs = []
                for inst in group_data['instances']:
                    instance_strs.append(f"{inst['object_name']}:{inst['property_path']}:{inst['color_space']}")
                item.object_name = f"{group_data['count']}|{group_data['hex']}|" + "|".join(instance_strs)
                
                # Restore live_sync: enabled if ANY instance had it
                item.live_sync = False
                for inst in group_data['instances']:
                    key = (inst['object_name'], inst['property_path'])
                    if saved_live_sync.get(key, False):
                        item.live_sync = True
                        break
                
                item.suppress_updates = False
            
            self.report({'INFO'}, f"Found {len(groups_data)} unique colors across {len(detected)} properties")
        
        return {'FINISHED'}


class OBJECT_COLORS_OT_pull(Operator):
    """Pull color from Coloraide to object property (↓)"""
    bl_idname = "object_colors.pull"
    bl_label = "Pull Color from Coloraide"
    bl_description = "Apply Coloraide's current color to this property"
    bl_options = {'INTERNAL'}
    
    index: IntProperty()
    
    @classmethod
    def poll(cls, context):
        if is_updating() or is_updating_live_sync():
            return False
        return True
    
    def execute(self, context):
        if is_updating() or is_updating_live_sync():
            return {'CANCELLED'}
        
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        if self.index >= len(obj_colors.items):
            return {'CANCELLED'}
        
        item = obj_colors.items[self.index]
        current_color = tuple(wm.coloraide_picker.mean)
        
        if item.property_path == '__GROUP__':
            # GROUPED: Pull to all instances
            parts = item.object_name.split('|')
            count = int(parts[0])
            instances = parts[2:]
            
            success = 0
            for inst_str in instances:
                obj_name, prop_path, color_space = inst_str.split(':')
                obj = bpy.data.objects.get(obj_name)
                if obj and set_color_value(obj, prop_path, current_color, color_space):
                    success += 1
            
            # Update item
            item.suppress_updates = True
            item.color = current_color
            item.suppress_updates = False
            
            # Update hex in label
            from ..COLORAIDE_colorspace import linear_to_hex
            new_hex = linear_to_hex(current_color)
            item.label_short = f"{new_hex} ({count}×)"
            item.object_name = f"{count}|{new_hex}|" + "|".join(instances)
            
            self.report({'INFO'}, f"Pulled to {success}/{count} instances")
            return {'FINISHED'}
        
        # OBJECT MODE: Pull to single property
        obj = bpy.data.objects.get(item.object_name)
        if not obj:
            return {'CANCELLED'}
        
        if set_color_value(obj, item.property_path, current_color, item.color_space):
            item.suppress_updates = True
            item.color = current_color
            item.suppress_updates = False
            return {'FINISHED'}
        
        return {'CANCELLED'}


class OBJECT_COLORS_OT_push(Operator):
    """Push color from object property to Coloraide (↑)"""
    bl_idname = "object_colors.push"
    bl_label = "Push Color to Coloraide"
    bl_description = "Load this color into Coloraide's picker"
    bl_options = {'INTERNAL'}
    
    index: IntProperty()
    
    @classmethod
    def poll(cls, context):
        if is_updating() or is_updating_live_sync():
            return False
        return True
    
    def execute(self, context):
        if is_updating() or is_updating_live_sync():
            return {'CANCELLED'}
        
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        if self.index >= len(obj_colors.items):
            return {'CANCELLED'}
        
        item = obj_colors.items[self.index]
        
        # For grouped items, use stored color
        if item.property_path == '__GROUP__':
            sync_all(context, 'object_colors', tuple(item.color))
            return {'FINISHED'}
        
        # OBJECT MODE: Read from object
        obj = bpy.data.objects.get(item.object_name)
        if not obj:
            return {'CANCELLED'}
        
        color = get_color_value(obj, item.property_path, item.color_space)
        if color:
            item.suppress_updates = True
            item.color = color
            item.suppress_updates = False
            sync_all(context, 'object_colors', color)
            return {'FINISHED'}
        
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
        if is_updating() or is_updating_live_sync():
            return False
        return True
    
    def execute(self, context):
        if is_updating() or is_updating_live_sync():
            return {'CANCELLED'}
        
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        if self.index >= len(obj_colors.items):
            return {'CANCELLED'}
        
        item = obj_colors.items[self.index]
        
        if item.property_path != '__GROUP__':
            return {'CANCELLED'}
        
        parts = item.object_name.split('|')
        count = int(parts[0])
        instances = parts[2:]
        
        new_color = tuple(item.color[:3])
        
        for inst_str in instances:
            obj_name, prop_path, color_space = inst_str.split(':')
            obj = bpy.data.objects.get(obj_name)
            if obj:
                set_color_value(obj, prop_path, new_color, color_space)
        
        # Update hex in label
        from ..COLORAIDE_colorspace import linear_to_hex
        new_hex = linear_to_hex(new_color)
        item.label_short = f"{new_hex} ({count}×)"
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
    """Update all properties with live sync enabled (uses cache)"""
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