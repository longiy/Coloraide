"""
Object color properties detection and management for Coloraide.
CLEAN REWRITE: Simplified with auto-refresh on mode switch.
"""

import bpy
from bpy.props import (BoolProperty, StringProperty, FloatVectorProperty, 
                       CollectionProperty, EnumProperty, IntProperty)
from bpy.types import PropertyGroup


class ColorPropertyItem(PropertyGroup):
    """Individual color property detected on an object"""
    
    suppress_updates: BoolProperty(
        name="Suppress Updates",
        description="Prevent update callbacks during refresh",
        default=False,
        options={'SKIP_SAVE', 'HIDDEN'}
    )
    
    label_short: StringProperty(
        name="Short Label",
        description="Short label for UI",
        default=""
    )
    
    label_detailed: StringProperty(
        name="Detailed Label", 
        description="Detailed label for tooltip",
        default=""
    )
    
    object_name: StringProperty(
        name="Object Name",
        description="Object this property belongs to",
        default=""
    )
    
    property_path: StringProperty(
        name="Property Path",
        description="Python path to access this property",
        default=""
    )
    
    property_type: StringProperty(
        name="Property Type",
        description="Type (GEONODES, MATERIAL, LIGHT, OBJECT, GPENCIL)",
        default=""
    )
    
    color_space: StringProperty(
        name="Color Space",
        description="Color space (LINEAR or COLOR_GAMMA)",
        default="LINEAR"
    )
    
    def update_color(self, context):
        """When user changes color, immediately write to object"""
        if self.suppress_updates:
            return
        
        from ..COLORAIDE_object_colors import set_color_value, clear_object_cache
        
        if self.property_path == '__GROUP__':
            # GROUPED: Update all instances
            parts = self.object_name.split('|')
            count = int(parts[0])
            instances = parts[2:] if len(parts) > 2 else []
            new_color = tuple(self.color[:3])
            
            for inst_str in instances:
                try:
                    obj_name, prop_path, color_space = inst_str.split(':')
                    obj = bpy.data.objects.get(obj_name)
                    if obj:
                        set_color_value(obj, prop_path, new_color, color_space)
                        clear_object_cache(obj_name)
                except Exception as e:
                    print(f"Coloraide: Error updating group instance: {e}")
            
            # Update hex label
            from ..COLORAIDE_colorspace import linear_to_hex
            new_hex = linear_to_hex(new_color)
            self.label_short = f"{new_hex} ({count}×)"
            self.object_name = f"{count}|{new_hex}|" + "|".join(instances)
            return
        
        # OBJECT MODE: Update single property
        obj = bpy.data.objects.get(self.object_name)
        if not obj:
            return
        
        color = tuple(self.color[:3])
        success = set_color_value(obj, self.property_path, color, self.color_space)
        
        if success:
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
    """Manager for detected object color properties"""
    
    def update_display_mode(self, context):
        """Auto-refresh when switching modes"""
        try:
            bpy.ops.object_colors.refresh()
        except:
            pass
    
    display_mode: EnumProperty(
        name="Display Mode",
        description="How to display detected colors",
        items=[
            ('OBJECT', "Object Mode", "Individual properties per object", 'OBJECT_DATA', 0),
            ('GROUPED', "Grouped Mode", "Group identical colors", 'COLOR', 1),
        ],
        default='OBJECT',
        update=update_display_mode
    )
    
    items: CollectionProperty(
        type=ColorPropertyItem,
        name="Color Properties"
    )
    
    show_multiple_objects: BoolProperty(
        name="Show Multiple Objects",
        description="Show colors from all selected objects (off = active only)",
        default=False
    )
    
    tolerance: bpy.props.FloatProperty(
        name="Color Tolerance",
        description="How similar colors must be to group",
        default=0.001,
        min=0.0,
        max=0.1,
        precision=4,
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    
    last_active_object: StringProperty(
        name="Last Active Object",
        default="",
        options={'SKIP_SAVE'}
    )
    
    last_selected_count: IntProperty(
        name="Last Selected Count",
        default=0,
        options={'SKIP_SAVE'}
    )