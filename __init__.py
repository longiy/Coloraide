"""
Main initialization file for Coloraide addon - Blender 5.0+ version.
With customizable tab category in preferences.
NOW WITH GROUPED COLOR MODE!
"""
import bpy
from bpy.app.handlers import persistent
from bpy.types import AddonPreferences
from bpy.props import StringProperty
from bpy.app.handlers import persistent

# First utilities and sync system from root
from .COLORAIDE_colorspace import *
from .COLORAIDE_mode_manager import ModeManager
from .COLORAIDE_utils import *
from .COLORAIDE_sync import sync_all, is_updating, update_lock
from .COLORAIDE_keymaps import register_keymaps, unregister_keymaps
from .COLORAIDE_brush_sync import (sync_coloraide_from_brush, update_brush_color, 
                                   is_brush_updating)
from .COLORAIDE_color_grouping import *  # NEW: Color grouping utilities

# Import all properties
from .properties.PALETTE_properties import ColoraidePaletteProperties
from .properties.NORMAL_properties import ColoraideNormalProperties
from .properties.CPICKER_properties import ColoraidePickerProperties
from .properties.CWHEEL_properties import ColoraideWheelProperties 
from .properties.HEX_properties import ColoraideHexProperties
from .properties.RGB_properties import ColoraideRGBProperties
from .properties.LAB_properties import ColoraideLABProperties
from .properties.HSV_properties import ColoraideHSVProperties
from .properties.CHISTORY_properties import ColoraideHistoryProperties, ColorHistoryItemProperties
from .COLORAIDE_properties import ColoraideDisplayProperties

# Import all operators and panels
from .operators.NORMAL_OT import NORMAL_OT_color_picker
from .operators.CPICKER_OT import IMAGE_OT_screen_picker, IMAGE_OT_quickpick, IMAGE_OT_screen_picker_quick
from .operators.HSV_OT import COLOR_OT_sync_hsv  
from .operators.RGB_OT import COLOR_OT_sync_rgb
from .operators.LAB_OT import COLOR_OT_sync_lab
from .operators.CWHEEL_OT import COLOR_OT_sync_wheel, COLOR_OT_reset_wheel_scale
from .operators.CHISTORY_OT import COLOR_OT_adjust_history_size, COLOR_OT_clear_history, COLOR_OT_reset_history_flags
from .operators.PALETTE_OT import PALETTE_OT_add_color, PALETTE_OT_remove_color
from .COLORAIDE_monitor import COLOR_OT_monitor
from .operators.HEX_OT import COLOR_OT_sync_hex

# Import all panels
from .panels.NORMAL_panel import draw_normal_panel
from .panels.CDYNAMICS_panel import draw_dynamics_panel
from .panels.CPICKER_panel import draw_picker_panel
from .panels.CWHEEL_panel import draw_wheel_panel  
from .panels.HEX_panel import draw_hex_panel
from .panels.RGB_panel import draw_rgb_panel
from .panels.LAB_panel import draw_lab_panel
from .panels.HSV_panel import draw_hsv_panel
from .panels.CHISTORY_panel import draw_history_panel
from .panels.PALETTE_panel import draw_palette_panel
from .COLORAIDE_panel import IMAGE_PT_coloraide, VIEW3D_PT_coloraide, CLIP_PT_coloraide

# UPDATED: Import updated object colors system
from .properties.OBJECT_COLORS_properties import ColorPropertyItem, ColoraideObjectColorsProperties
from .operators.OBJECT_COLORS_OT import (OBJECT_COLORS_OT_refresh, OBJECT_COLORS_OT_pull, 
                                          OBJECT_COLORS_OT_push, OBJECT_COLORS_OT_update_group_color,
                                          OBJECT_COLORS_OT_show_tooltip)
from .panels.OBJECT_COLORS_panel import draw_object_colors_panel

bl_info = {
    'name': 'Coloraide',
    'author': 'longiy',
    'version': (1, 5, 0),  # Version bump for grouped colors feature
    'blender': (5, 0, 0),
    'location': '(Image Editor, Clip Editor, and 3D View) -> Color',
    'description': 'Advanced color picker with extended features for Blender 5.0+',
    'warning': 'Requires Blender 5.0 or newer - uses native color jitter API',
    'doc_url': '',
    'category': 'Paint',
}

# Define panel classes for tab customization
panels = (
    IMAGE_PT_coloraide,
    VIEW3D_PT_coloraide,
    CLIP_PT_coloraide,
)


def update_panel(self, context):
    """Update panel tab category when changed in preferences"""
    message = "Coloraide: Updating Panel locations has failed"
    try:
        # Unregister all panels
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        # Update category and re-register
        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass


class ColoraideAddonPreferences(AddonPreferences):
    """Addon preferences for Coloraide - allows customizing panel tab location"""
    bl_idname = __name__

    category: StringProperty(
        name="Tab Category",
        description="Choose the sidebar tab where Coloraide panels will appear",
        default="Coloraide",
        update=update_panel
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.label(text="Sidebar Tab Category:")
        col.prop(self, "category", text="")
        
        # Add helpful info
        box = layout.box()
        box.label(text="This controls which tab the Coloraide panel appears in.", icon='INFO')
        box.label(text="Default: 'Coloraide' - Change to 'Tool', 'View', 'Edit', etc.")
        box.label(text="Applies to Image Editor, 3D View, and Clip Editor.")


# Collect all classes that need registration
classes = [
    # Properties
    ColorPropertyItem,  # Before ColoraideObjectColorsProperties
    ColoraideObjectColorsProperties,

    ColoraidePaletteProperties,
    ColoraideNormalProperties,
    ColoraideDisplayProperties,
    ColoraidePickerProperties,
    ColoraideWheelProperties,
    ColoraideHexProperties,
    ColoraideRGBProperties,
    ColoraideLABProperties,
    ColoraideHSVProperties,
    ColorHistoryItemProperties,  # Register before ColoraideHistoryProperties
    ColoraideHistoryProperties,
    
    # Operators
    OBJECT_COLORS_OT_refresh,
    OBJECT_COLORS_OT_pull,
    OBJECT_COLORS_OT_push,
    OBJECT_COLORS_OT_update_group_color,  # NEW: Group color update operator
    OBJECT_COLORS_OT_show_tooltip,  # NEW: Tooltip operator for grouped mode

    NORMAL_OT_color_picker,
    IMAGE_OT_screen_picker,
    IMAGE_OT_screen_picker_quick,
    IMAGE_OT_quickpick,
    COLOR_OT_sync_hex,
    COLOR_OT_sync_hsv,
    COLOR_OT_sync_rgb,
    COLOR_OT_sync_lab,
    COLOR_OT_sync_wheel,
    COLOR_OT_reset_wheel_scale,
    COLOR_OT_adjust_history_size,
    COLOR_OT_clear_history,
    PALETTE_OT_add_color,
    PALETTE_OT_remove_color,
    COLOR_OT_monitor,
    COLOR_OT_reset_history_flags,
    
    # Preferences (must be registered before panels for update_panel to work)
    ColoraideAddonPreferences,
    
    # Panels - will be registered via update_panel()
    # IMAGE_PT_coloraide,
    # VIEW3D_PT_coloraide,
    # CLIP_PT_coloraide,
]

def start_color_monitor():
    """Start the color monitor modal operator"""
    bpy.ops.color.monitor('INVOKE_DEFAULT')
    return None  # Important: Return None to prevent timer error

@persistent
def load_handler(dummy):
    """Ensure color monitor is running after file load"""
    # Small delay to ensure context is ready
    bpy.app.timers.register(start_color_monitor, first_interval=0.1)

def initialize_addon(context):
    """Initialize addon state after registration. Enhanced for Image Editor."""
    if not context or not context.window_manager:
        return
    
    wm = context.window_manager
    
    # Initialize color history
    if hasattr(wm, 'coloraide_history'):
        wm.coloraide_history.initialize_history()
    
    # Try to initialize from current brush color immediately
    try:
        from .COLORAIDE_mode_manager import ModeManager
        from .COLORAIDE_brush_sync import sync_coloraide_from_brush
        
        current_mode = ModeManager.get_current_mode(context)
        if current_mode:
            brush_color = ModeManager.get_brush_color(context)
            if brush_color:
                sync_coloraide_from_brush(context, brush_color)
                print("Coloraide: Initialized with brush color")
    except Exception as e:
        print(f"Coloraide initialization warning: {e}")

@persistent
def selection_change_handler(scene, depsgraph):
    """Auto-refresh object colors when selection changes"""
    try:
        context = bpy.context
        if not context or not context.window_manager:
            return
        
        wm = context.window_manager
        if not hasattr(wm, 'coloraide_object_colors'):
            return
        
        obj_colors = wm.coloraide_object_colors
        
        # Only refresh if Object Colors panel is visible
        if not wm.coloraide_display.show_object_colors:
            return
        
        # Check if selection changed
        active_obj = context.active_object
        active_name = active_obj.name if active_obj else ""
        selected_count = len(context.selected_objects)
        
        # Detect changes
        changed = (
            active_name != obj_colors.last_active_object or
            selected_count != obj_colors.last_selected_count
        )
        
        if changed and (active_obj or selected_count > 0):
            # Update tracking
            obj_colors.last_active_object = active_name
            obj_colors.last_selected_count = selected_count
            
            # Auto-refresh colors
            bpy.ops.object_colors.refresh()
    except:
        pass  # Silent fail to avoid breaking Blender

def register():
    # Register non-panel classes first
    for cls in classes:
        bpy.utils.register_class(cls)
        
    # Register keymaps
    register_keymaps()
    
    # Register property group assignments
    bpy.types.WindowManager.coloraide_object_colors = bpy.props.PointerProperty(type=ColoraideObjectColorsProperties)
    
    bpy.types.WindowManager.coloraide_palette = bpy.props.PointerProperty(type=ColoraidePaletteProperties)
    bpy.types.WindowManager.coloraide_normal = bpy.props.PointerProperty(type=ColoraideNormalProperties)
    bpy.types.WindowManager.coloraide_display = bpy.props.PointerProperty(type=ColoraideDisplayProperties)
    bpy.types.WindowManager.coloraide_picker = bpy.props.PointerProperty(type=ColoraidePickerProperties)
    bpy.types.WindowManager.coloraide_wheel = bpy.props.PointerProperty(type=ColoraideWheelProperties)
    bpy.types.WindowManager.coloraide_hex = bpy.props.PointerProperty(type=ColoraideHexProperties)
    bpy.types.WindowManager.coloraide_rgb = bpy.props.PointerProperty(type=ColoraideRGBProperties)
    bpy.types.WindowManager.coloraide_lab = bpy.props.PointerProperty(type=ColoraideLABProperties)
    bpy.types.WindowManager.coloraide_hsv = bpy.props.PointerProperty(type=ColoraideHSVProperties)
    bpy.types.WindowManager.coloraide_history = bpy.props.PointerProperty(type=ColoraideHistoryProperties)
    
    # Register panels with correct category from preferences
    update_panel(None, bpy.context)
    
    # Add load handler
    bpy.app.handlers.load_post.append(load_handler)
    # Add selection change handler
    bpy.app.handlers.depsgraph_update_post.append(selection_change_handler)
    
    # Initialize addon
    initialize_addon(bpy.context)
    
    # Start color monitor after slight delay
    bpy.app.timers.register(start_color_monitor, first_interval=0.1)
    
    print("✓ Coloraide registered with Grouped Color Mode support")

def unregister():
    # Remove selection handler
    if selection_change_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(selection_change_handler)

    # Remove load handler
    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)
    
    # Unregister keymaps
    unregister_keymaps()
    
    # Unregister panels first (in case they were registered separately)
    for panel in panels:
        try:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)
        except:
            pass
    
    # Unregister property groups
    del bpy.types.WindowManager.coloraide_object_colors

    del bpy.types.WindowManager.coloraide_palette
    del bpy.types.WindowManager.coloraide_normal
    del bpy.types.WindowManager.coloraide_history
    del bpy.types.WindowManager.coloraide_hsv
    del bpy.types.WindowManager.coloraide_lab
    del bpy.types.WindowManager.coloraide_rgb
    del bpy.types.WindowManager.coloraide_hex
    del bpy.types.WindowManager.coloraide_wheel
    del bpy.types.WindowManager.coloraide_picker
    del bpy.types.WindowManager.coloraide_display
    
    # Unregister other classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("✓ Coloraide unregistered")

if __name__ == "__main__":
    register()