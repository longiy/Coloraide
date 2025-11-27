"""
Object color properties detection and management for Coloraide.
Stores detected color properties from selected objects.
"""

import bpy
from bpy.props import BoolProperty, StringProperty, FloatVectorProperty, CollectionProperty
from bpy.types import PropertyGroup


class ColorPropertyItem(PropertyGroup):
    """Individual color property detected on an object"""
    
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
        description="Type of property (GEONODES, MATERIAL, LIGHT, OBJECT)",
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
        from ..COLORAIDE_object_colors import set_color_value
        import bpy
        
        # Find object
        obj = bpy.data.objects.get(self.object_name)
        if not obj:
            return
        
        # Push color to object (scene linear → correct space)
        color = tuple(self.color[:3])
        set_color_value(obj, self.property_path, color, self.color_space)
    
    # Current color value (cached for display, always in scene linear)
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
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