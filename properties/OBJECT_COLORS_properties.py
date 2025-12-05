"""
Object color properties detection and management for Coloraide.
NOW WITH MODE TOGGLE: Object Mode vs Grouped Mode
FIX: Removed auto-refresh from mode toggles - user must click Rescan explicitly
"""

import bpy
from bpy.props import (BoolProperty, StringProperty, FloatVectorProperty, 
                       CollectionProperty, EnumProperty, IntProperty, PointerProperty)
from bpy.types import PropertyGroup


class ColorPropertyItem(PropertyGroup):
    """Individual color property detected on an object (Object Mode)"""
    
    suppress_updates: BoolProperty(
        name="Suppress Updates",
        description="Prevent update callbacks during refresh operations",
        default=False,
        options={'SKIP_SAVE', 'HIDDEN'}
    )
    
    label_short: StringProperty(
        name="Short Label",
        description="Short label for UI display",
        default=""
    )
    
    label_detailed: StringProperty(
        name="Detailed Label", 
        description="Detailed label for tooltip",
        default=""
    )
    
    object_name: StringProperty(
        name="Object Name",
        description="Name of the object this property belongs to",
        default=""
    )
    
    property_path: StringProperty(
        name="Property Path",
        description="Python path to access this property",
        default=""
    )
    
    property_type: StringProperty(
        name="Property Type",
        description="Type of property (GEONODES, MATERIAL, LIGHT, OBJECT, GPENCIL)",
        default=""
    )
    
    color_space: StringProperty(
        name="Color Space",
        description="Color space this property is stored in (LINEAR or SRGB)",
        default="LINEAR"
    )
    
    def update_color(self, context):
        """
        When user changes color swatch, IMMEDIATELY push to object.
        This ensures manual changes persist through rescans.
        """
        if self.suppress_updates:
            return
        
        # Import here to avoid circular dependencies
        from ..COLORAIDE_object_colors import set_color_value, clear_object_cache
        
        # Check if this is a grouped item
        if self.property_path == '__GROUP__':
            # GROUPED MODE: Update all instances directly
            parts = self.object_name.split('|')
            count = int(parts[0])
            instances = parts[2:] if len(parts) > 2 else []
            
            new_color = tuple(self.color[:3])
            
            for inst_str in instances:
                try:
                    obj_name, prop_path, color_space = inst_str.split(':')
                    obj = bpy.data.objects.get(obj_name)
                    if obj:
                        # CRITICAL: Write to object so rescan picks it up
                        set_color_value(obj, prop_path, new_color, color_space)
                        # CRITICAL: Clear cache for this object
                        clear_object_cache(obj_name)
                except Exception as e:
                    print(f"Coloraide: Error updating grouped instance: {e}")
            
            # Update hex value in label
            from ..COLORAIDE_colorspace import linear_to_hex
            new_hex = linear_to_hex(new_color)
            self.label_short = f"{new_hex} ({count}×)"
            
            # Update stored data
            self.object_name = f"{count}|{new_hex}|" + "|".join(instances)
            return
        
        # OBJECT MODE: Update single property
        obj = bpy.data.objects.get(self.object_name)
        if not obj:
            return
        
        color = tuple(self.color[:3])
        
        # CRITICAL: Write to object immediately so rescan sees the change
        success = set_color_value(obj, self.property_path, color, self.color_space)
        
        if success:
            # CRITICAL: Clear cache for this object so next scan reads fresh data
            clear_object_cache(self.object_name)
        else:
            print(f"Coloraide: Failed to write color to {self.property_path}")
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        default=(0.5, 0.5, 0.5),
        update=update_color
    )
    
    live_sync: BoolProperty(
        name="Live Sync",
        description="Sync Coloraide changes to this property in real-time",
        default=False
    )


class ColoraideObjectColorsProperties(PropertyGroup):
    """Manager for detected object color properties with mode toggle"""
    
    def update_display_mode(self, context):
        """
        When switching modes, rebuild display from cached scan data.
        This avoids expensive rescan while still showing correct UI.
        """
        # Check if we have items to rebuild
        if not self.items:
            return
        
        # Save current items as "raw" scan data
        raw_data = []
        for item in self.items:
            if item.property_path != '__GROUP__':
                # Regular item - save as-is
                raw_data.append({
                    'label_short': item.label_short,
                    'label_detailed': item.label_detailed,
                    'object_name': item.object_name,
                    'property_path': item.property_path,
                    'property_type': item.property_type,
                    'color_space': item.color_space,
                    'color': tuple(item.color[:3]),
                    'live_sync': item.live_sync
                })
            else:
                # Grouped item - extract individual instances
                parts = item.object_name.split('|')
                instances = parts[2:] if len(parts) > 2 else []
                group_color = tuple(item.color[:3])
                group_live_sync = item.live_sync
                
                for inst_str in instances:
                    try:
                        obj_name, prop_path, color_space = inst_str.split(':')
                        # We don't have the original label, so reconstruct basic one
                        raw_data.append({
                            'label_short': f"{obj_name}:{prop_path.split('.')[-1][:20]}",
                            'label_detailed': f"{obj_name} > {prop_path}",
                            'object_name': obj_name,
                            'property_path': prop_path,
                            'property_type': 'UNKNOWN',
                            'color_space': color_space,
                            'color': group_color,
                            'live_sync': group_live_sync
                        })
                    except:
                        pass
        
        # If we extracted no raw data, skip rebuild
        if not raw_data:
            return
        
        # Rebuild based on new mode
        self.items.clear()
        
        if self.display_mode == 'OBJECT':
            # Rebuild as individual items
            for data in raw_data:
                item = self.items.add()
                item.suppress_updates = True
                item.label_short = data['label_short']
                item.label_detailed = data['label_detailed']
                item.object_name = data['object_name']
                item.property_path = data['property_path']
                item.property_type = data['property_type']
                item.color_space = data['color_space']
                item.color = data['color']
                item.live_sync = data.get('live_sync', False)
                item.suppress_updates = False
        
        else:  # GROUPED
            # Rebuild as grouped items
            from ..COLORAIDE_color_grouping import group_colors_by_value
            
            # Convert raw_data to format group_colors_by_value expects
            detected_colors = []
            for data in raw_data:
                detected_colors.append({
                    'label_short': data['label_short'],
                    'label_detailed': data['label_detailed'],
                    'object_name': data['object_name'],
                    'property_path': data['property_path'],
                    'property_type': data['property_type'],
                    'color_space': data['color_space'],
                    'color': data['color']
                })
            
            groups_data = group_colors_by_value(detected_colors, self.tolerance)
            
            for group_data in groups_data:
                item = self.items.add()
                item.suppress_updates = True
                item.label_short = f"{group_data['hex']} ({group_data['count']}×)"
                item.label_detailed = f"Color group: {group_data['count']} instances"
                item.property_path = '__GROUP__'
                
                # Build instance data string
                instance_strs = []
                for inst in group_data['instances']:
                    instance_strs.append(f"{inst['object_name']}:{inst['property_path']}:{inst['color_space']}")
                item.object_name = f"{group_data['count']}|{group_data['hex']}|" + "|".join(instance_strs)
                item.color = group_data['color']
                
                # Preserve live_sync from original data (all instances in group should have same setting)
                # Use first instance's live_sync state
                if group_data['instances']:
                    first_inst = group_data['instances'][0]
                    # Find matching raw_data entry
                    for data in raw_data:
                        if (data['object_name'] == first_inst['object_name'] and 
                            data['property_path'] == first_inst['property_path']):
                            item.live_sync = data.get('live_sync', False)
                            break
                
                item.suppress_updates = False
    
    # MODE SELECTION - NOW WITH AUTO-REBUILD
    display_mode: EnumProperty(
        name="Display Mode",
        description="How to display detected colors",
        items=[
            ('OBJECT', "Object Mode", "Show individual properties per object", 'OBJECT_DATA', 0),
            ('GROUPED', "Grouped Mode", "Group identical colors (Figma-style)", 'COLOR', 1),
        ],
        default='OBJECT',
        update=update_display_mode  # RE-ADDED: Now rebuilds display without rescanning
    )
    
    # OBJECT MODE: Collection of individual properties
    items: CollectionProperty(
        type=ColorPropertyItem,
        name="Color Properties"
    )
    
    # MULTI SELECTION - NO AUTO-REFRESH
    show_multiple_objects: BoolProperty(
        name="Show Multiple Objects",
        description="Show colors from all selected objects (off = active object only)",
        default=False
        # REMOVED: update=update_show_multiple
    )
    
    # Tolerance for grouped mode (HIDDEN - no UI control)
    tolerance: bpy.props.FloatProperty(
        name="Color Tolerance",
        description="How similar colors must be to group together",
        default=0.001,
        min=0.0,
        max=0.1,
        soft_min=0.0,
        soft_max=0.05,
        precision=4,
        step=0.01,
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    
    # Internal state tracking
    last_active_object: StringProperty(
        name="Last Active Object",
        description="Name of last active object (for change detection)",
        default="",
        options={'SKIP_SAVE'}
    )
    
    last_selected_count: IntProperty(
        name="Last Selected Count",
        description="Number of last selected objects (for change detection)",
        default=0,
        options={'SKIP_SAVE'}
    )