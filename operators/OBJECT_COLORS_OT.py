"""
Operators for object color property management in Coloraide.
"""

import bpy
from bpy.types import Operator
from bpy.props import IntProperty
from ..COLORAIDE_object_colors import scan_all_colors, get_color_value, set_color_value
from ..COLORAIDE_sync import sync_all


class OBJECT_COLORS_OT_refresh(Operator):
    """Refresh detected color properties from selected objects"""
    bl_idname = "object_colors.refresh"
    bl_label = "Refresh Object Colors"
    bl_description = "Scan selected objects for color properties"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        # Clear existing items
        obj_colors.items.clear()
        
        # Scan for colors
        detected = scan_all_colors(context, obj_colors.show_multiple_objects)
        
        # Add to collection
        for color_data in detected:
            item = obj_colors.items.add()
            item.label_short = color_data['label_short']
            item.label_detailed = color_data['label_detailed']
            item.object_name = color_data['object_name']
            item.property_path = color_data['property_path']
            item.property_type = color_data['property_type']
            item.color_space = color_data.get('color_space', 'LINEAR')
            item.color = color_data['color']  # Already converted to linear by scan functions
            item.live_sync = False
        
        self.report({'INFO'}, f"Found {len(detected)} color properties")
        return {'FINISHED'}


class OBJECT_COLORS_OT_pull(Operator):
    """Pull color from object property to Coloraide (↓)"""
    bl_idname = "object_colors.pull"
    bl_label = "Pull Color to Coloraide"
    bl_description = "Load this color into Coloraide's picker"
    bl_options = {'INTERNAL'}
    
    index: IntProperty()
    
    def execute(self, context):
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        if self.index >= len(obj_colors.items):
            self.report({'WARNING'}, "Invalid index")
            return {'CANCELLED'}
        
        item = obj_colors.items[self.index]
        
        # Find object
        obj = bpy.data.objects.get(item.object_name)
        if not obj:
            self.report({'WARNING'}, f"Object '{item.object_name}' not found")
            return {'CANCELLED'}
        
        # Get current color value (returns scene linear)
        color = get_color_value(obj, item.property_path, item.color_space)
        if color:
            # Update cached color in item
            item.color = color
            # Sync to Coloraide (already in scene linear)
            sync_all(context, 'object_colors', color)
            self.report({'INFO'}, f"Pulled {item.label_short}: {color}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, f"Failed to read color from {item.property_path}")
            return {'CANCELLED'}


class OBJECT_COLORS_OT_push(Operator):
    """Push color from Coloraide to object property (↑)"""
    bl_idname = "object_colors.push"
    bl_label = "Push Color from Coloraide"
    bl_description = "Apply Coloraide's current color to this property"
    bl_options = {'INTERNAL'}
    
    index: IntProperty()
    
    def execute(self, context):
        wm = context.window_manager
        obj_colors = wm.coloraide_object_colors
        
        if self.index >= len(obj_colors.items):
            self.report({'WARNING'}, "Invalid index")
            return {'CANCELLED'}
        
        item = obj_colors.items[self.index]
        
        # Find object
        obj = bpy.data.objects.get(item.object_name)
        if not obj:
            self.report({'WARNING'}, f"Object '{item.object_name}' not found")
            return {'CANCELLED'}
        
        # Get Coloraide's current color (scene linear)
        current_color = tuple(wm.coloraide_picker.mean)
        
        # Set color on object (converts to correct space if needed)
        success = set_color_value(obj, item.property_path, current_color, item.color_space)
        if success:
            # Update cached color
            item.color = current_color
            self.report({'INFO'}, f"Pushed to {item.label_short}: {current_color}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, f"Failed to set color at {item.property_path}")
            return {'CANCELLED'}


def update_live_synced_properties(context, color):
    """
    Update all properties with live sync enabled.
    
    Args:
        color: Scene linear RGB tuple (r, g, b)
    """
    wm = context.window_manager
    obj_colors = wm.coloraide_object_colors
    
    updated_count = 0
    failed_count = 0
    
    for item in obj_colors.items:
        if not item.live_sync:
            continue
        
        # Find object
        obj = bpy.data.objects.get(item.object_name)
        if not obj:
            failed_count += 1
            continue
        
        # Set color (converts to correct space if needed)
        if set_color_value(obj, item.property_path, color, item.color_space):
            item.color = color
            updated_count += 1
        else:
            failed_count += 1
    
    # Optional: print debug info (remove in production)
    if updated_count > 0 or failed_count > 0:
        print(f"Live sync: {updated_count} updated, {failed_count} failed")


__all__ = [
    'OBJECT_COLORS_OT_refresh',
    'OBJECT_COLORS_OT_pull',
    'OBJECT_COLORS_OT_push',
    'update_live_synced_properties'
]