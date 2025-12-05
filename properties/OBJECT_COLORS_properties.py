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
            print(f"Coloraide DEBUG: update_color skipped (suppress_updates=True)")
            return
        
        print(f"Coloraide DEBUG: update_color called for {self.label_short}")
        
        # Import here to avoid circular dependencies
        from ..COLORAIDE_object_colors import set_color_value, clear_object_cache
        
        # Check if this is a grouped item
        if self.property_path == '__GROUP__':
            # GROUPED MODE: Update all instances directly
            parts = self.object_name.split('|')
            count = int(parts[0])
            instances = parts[2:] if len(parts) > 2 else []
            
            new_color = tuple(self.color[:3])
            print(f"Coloraide DEBUG: Updating {len(instances)} instances in group to {new_color}")
            
            for inst_str in instances:
                try:
                    obj_name, prop_path, color_space = inst_str.split(':')
                    obj = bpy.data.objects.get(obj_name)
                    if obj:
                        # CRITICAL: Write to object so rescan picks it up
                        success = set_color_value(obj, prop_path, new_color, color_space)
                        if success:
                            # CRITICAL: Clear cache for this object
                            clear_object_cache(obj_name)
                            print(f"Coloraide DEBUG: Updated {obj_name}:{prop_path}")
                        else:
                            print(f"Coloraide DEBUG: FAILED to update {obj_name}:{prop_path}")
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
            print(f"Coloraide DEBUG: Object '{self.object_name}' not found!")
            return
        
        color = tuple(self.color[:3])
        print(f"Coloraide DEBUG: Writing color {color} to {self.object_name}:{self.property_path}")
        
        # CRITICAL: Write to object immediately so rescan sees the change
        success = set_color_value(obj, self.property_path, color, self.color_space)
        
        if success:
            # CRITICAL: Clear cache for this object so next scan reads fresh data
            clear_object_cache(self.object_name)
            print(f"Coloraide DEBUG: Successfully updated and cleared cache for {self.object_name}")
        else:
            print(f"Coloraide DEBUG: FAILED to write color to {self.property_path}")
    
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
    
    # MODE SELECTION - NO AUTO-REFRESH
    display_mode: EnumProperty(
        name="Display Mode",
        description="How to display detected colors",
        items=[
            ('OBJECT', "Object Mode", "Show individual properties per object", 'OBJECT_DATA', 0),
            ('GROUPED', "Grouped Mode", "Group identical colors (Figma-style)", 'COLOR', 1),
        ],
        default='OBJECT'
        # REMOVED: update=update_display_mode
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