"""
Object color properties detection and management for Coloraide.
NOW WITH MODE TOGGLE: Object Mode vs Grouped Mode
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
        """When user changes color swatch, push to object"""
        if self.suppress_updates:
            return
        
        # Check if this is a grouped item
        if self.property_path == '__GROUP__':
            # For grouped items, call the update operator
            # This ensures all instances get updated
            try:
                # Find our index in the items collection
                obj_colors = context.window_manager.coloraide_object_colors
                for idx, item in enumerate(obj_colors.items):
                    if item == self:
                        bpy.ops.object_colors.update_group_color(index=idx)
                        return
            except:
                pass
            return
        
        # OBJECT MODE: Update single property
        from ..COLORAIDE_object_colors import set_color_value
        
        obj = bpy.data.objects.get(self.object_name)
        if not obj:
            return
        
        color = tuple(self.color[:3])
        set_color_value(obj, self.property_path, color, self.color_space)
    
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
        """Auto-refresh when switching modes"""
        # Automatically refresh the color list when mode changes
        try:
            bpy.ops.object_colors.refresh()
        except:
            pass  # Silent fail if context not ready
    
    # MODE SELECTION
    display_mode: EnumProperty(
        name="Display Mode",
        description="How to display detected colors",
        items=[
            ('OBJECT', "Object Mode", "Show individual properties per object", 'OBJECT_DATA', 0),
            ('GROUPED', "Grouped Mode", "Group identical colors (Figma-style)", 'COLOR', 1),
        ],
        default='OBJECT',
        update=update_display_mode  # Auto-refresh on change
    )
    
    # OBJECT MODE: Collection of individual properties
    items: CollectionProperty(
        type=ColorPropertyItem,
        name="Color Properties"
    )
    
    # Settings
    def update_show_multiple(self, context):
        """Auto-refresh when toggling Multi on/off"""
        try:
            bpy.ops.object_colors.refresh()
        except:
            pass
    
    show_multiple_objects: BoolProperty(
        name="Show Multiple Objects",
        description="Show colors from all selected objects (off = active object only)",
        default=False,
        update=update_show_multiple  # Auto-refresh on toggle
    )
    
    # Tolerance for grouped mode (HIDDEN - no UI control)
    tolerance: bpy.props.FloatProperty(
        name="Color Tolerance",
        description="How similar colors must be to group together (0 = exact match, higher = more grouping)",
        default=0.001,  # Very precise - groups visually identical colors
        min=0.0,
        max=0.1,
        soft_min=0.0,
        soft_max=0.05,
        precision=4,
        step=0.01,
        options={'HIDDEN', 'SKIP_SAVE'}  # Hidden from UI, not saved
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