"""
Object color properties detection and management for Coloraide.
Stores detected color properties from selected objects.
"""

import bpy
from bpy.props import BoolProperty, StringProperty, FloatVectorProperty, CollectionProperty
from bpy.types import PropertyGroup


class ColorPropertyItem(PropertyGroup):
    """Individual color property detected on an object"""
    
    # Add suppress flag to prevent callback loops
    suppress_updates: BoolProperty(
        name="Suppress Updates",
        description="Prevent update callbacks during refresh operations",
        default=False,
        options={'SKIP_SAVE', 'HIDDEN'}
    )
    
    # Display info
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
    
    # Property path for access
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
    
    # Color space info
    color_space: StringProperty(
        name="Color Space",
        description="Color space this property is stored in (LINEAR or SRGB)",
        default="LINEAR"
    )
    
    def update_color(self, context):
        """When user changes color swatch, push to object"""
        # CRITICAL: Check suppress flag to prevent callback loops during refresh
        if self.suppress_updates:
            return
        
        print(f"\n{'='*60}")
        print(f"COLOR PROPERTY UPDATE CALLBACK TRIGGERED")
        print(f"{'='*60}")
        print(f"Property: {self.label_short}")
        print(f"Path: {self.property_path}")
        print(f"Color space: {self.color_space}")
        
        from ..COLORAIDE_object_colors import set_color_value
        from ..COLORAIDE_colorspace import linear_to_hex
        import bpy
        
        # Find object
        obj = bpy.data.objects.get(self.object_name)
        if not obj:
            print(f"ERROR: Object '{self.object_name}' not found")
            print(f"{'='*60}\n")
            return
        
        # Get color from property
        color = tuple(self.color[:3])
        print(f"Color from property (scene linear): {color}")
        print(f"  As hex: {linear_to_hex(color)}")
        
        # Push color to object (scene linear → correct space)
        success = set_color_value(obj, self.property_path, color, self.color_space)
        print(f"Set color result: {'SUCCESS' if success else 'FAILED'}")
        print(f"{'='*60}\n")
    
    # Current color value (cached for display, always in scene linear)
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',  # REVERTED: Tells Blender values are scene linear
        size=3,
        min=0.0, max=1.0,
        default=(0.5, 0.5, 0.5),
        update=update_color
    )
    
    # Live sync state
    live_sync: BoolProperty(
        name="Live Sync",
        description="Sync Coloraide changes to this property in real-time",
        default=False
    )


class ColoraideObjectColorsProperties(PropertyGroup):
    """Manager for detected object color properties"""
    
    # Collection of detected properties
    items: CollectionProperty(
        type=ColorPropertyItem,
        name="Color Properties"
    )
    
    # Settings
    show_multiple_objects: BoolProperty(
        name="Show Multiple Objects",
        description="Show colors from all selected objects (off = active object only)",
        default=False
    )
    
    # Internal state
    last_active_object: StringProperty(
        name="Last Active Object",
        description="Name of last active object (for change detection)",
        default="",
        options={'SKIP_SAVE'}
    )
    
    last_selected_count: bpy.props.IntProperty(
        name="Last Selected Count",
        description="Number of last selected objects (for change detection)",
        default=0,
        options={'SKIP_SAVE'}
    )