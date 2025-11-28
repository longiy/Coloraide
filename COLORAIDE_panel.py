"""
Main panel implementation for Coloraide addon.
Integrates all component panels including the new native color dynamics.
"""

import bpy
from bpy.types import Panel

# Import all panel drawing functions
from .panels.NORMAL_panel import draw_normal_panel
from .panels.CDYNAMICS_panel import draw_dynamics_panel
from .panels.CPICKER_panel import draw_picker_panel
from .panels.CWHEEL_panel import draw_wheel_panel
from .panels.RGB_panel import draw_rgb_panel
from .panels.LAB_panel import draw_lab_panel
from .panels.HSV_panel import draw_hsv_panel
from .panels.HEX_panel import draw_hex_panel
from .panels.CHISTORY_panel import draw_history_panel
from .panels.PALETTE_panel import draw_palette_panel
from .panels.OBJECT_COLORS_panel import draw_object_colors_panel

def draw_coloraide_panels(self, context):
    """Draw all Coloraide panels in the specified order, respecting preferences"""
    wm = context.window_manager
    if not hasattr(wm, 'coloraide_display'):
        return
    
    layout = self.layout
    
    # Try to get addon preferences, fallback to all enabled if fails
    try:
        # Get the correct addon identifier by finding which addon registered this module
        # This works for both legacy addons and extensions
        addon_prefs = None
        for addon in context.preferences.addons:
            if hasattr(addon.module, '__package__'):
                # Check if this module belongs to the addon
                if __name__.startswith(addon.module):
                    addon_prefs = addon.preferences
                    break
        
        # Fallback: try direct lookup (legacy addon path)
        if addon_prefs is None:
            module_parts = __name__.split('.')
            # Try to find the root module name
            for i in range(len(module_parts)):
                try:
                    test_name = '.'.join(module_parts[:i+1])
                    addon_prefs = context.preferences.addons[test_name].preferences
                    break
                except KeyError:
                    continue
        
        if addon_prefs is None:
            raise KeyError("Could not find addon preferences")
        
        prefs = addon_prefs
        
        # Check if preferences have the new properties
        if not hasattr(prefs, 'enable_color_wheel'):
            raise AttributeError("Preferences not updated")
            
    except (KeyError, AttributeError) as e:
        # Fallback: enable everything if preferences aren't accessible
        print(f"Coloraide: Could not access preferences ({e}), showing all panels")
        
        # Create a simple object with all enables set to True
        class FallbackPrefs:
            enable_color_wheel = True
            enable_color_dynamics = True
            enable_color_picker = True
            enable_color_sliders = True
            enable_history = True
            enable_palettes = True
            enable_object_colors = True
        
        prefs = FallbackPrefs()
    
    # 1. Draw color wheel (if enabled in preferences)
    if prefs.enable_color_wheel:
        draw_wheel_panel(layout, context)
    
    # 2. Draw color dynamics (if enabled in preferences)
    if prefs.enable_color_dynamics:
        draw_dynamics_panel(layout, context)

    # 3. Draw core color picker (if enabled in preferences)
    if prefs.enable_color_picker:
        draw_picker_panel(layout, context)
    
    # 4. Color spaces box (if enabled in preferences)
    if prefs.enable_color_sliders:
        box = layout.box()
        row = box.row()
        row.prop(wm.coloraide_display, "show_color_sliders", 
            text="Color Sliders", 
            icon='TRIA_DOWN' if wm.coloraide_display.show_color_sliders else 'TRIA_RIGHT',
            emboss=False
        )
        
        if wm.coloraide_display.show_color_sliders:
            # Color space toggles
            row = box.row(align=True)
            row.prop(wm.coloraide_display, "show_hsv_sliders", text="HSV", toggle=True)
            row.prop(wm.coloraide_display, "show_rgb_sliders", text="RGB", toggle=True)
            row.prop(wm.coloraide_display, "show_lab_sliders", text="LAB", toggle=True)
            
            # Draw slider panels directly without their boxes
            col = box.column()
            if wm.coloraide_display.show_rgb_sliders:
                draw_rgb_panel(col, context)
            if wm.coloraide_display.show_lab_sliders:
                draw_lab_panel(col, context)
            if wm.coloraide_display.show_hsv_sliders:
                draw_hsv_panel(col, context)
    
    # 5. Draw color history (if enabled in preferences)
    if prefs.enable_history:
        draw_history_panel(layout, context)
    
    # 6. Draw palettes (if enabled in preferences)
    if prefs.enable_palettes:
        draw_palette_panel(layout, context)

    # 7. Draw object colors (if enabled in preferences)
    if prefs.enable_object_colors:
        draw_object_colors_panel(layout, context)

class IMAGE_PT_coloraide(Panel):
    bl_label = "Coloraide 1.5.0"
    bl_idname = "IMAGE_PT_coloraide"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Coloraide"
    
    def draw(self, context):
        draw_coloraide_panels(self, context)

class VIEW3D_PT_coloraide(Panel):
    bl_label = "Coloraide 1.5.0"
    bl_idname = "VIEW3D_PT_coloraide"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Coloraide"
    
    @classmethod
    def poll(cls, context):
        return context.mode in {
            'PAINT_TEXTURE', 
            'PAINT_VERTEX', 
            'PAINT_GREASE_PENCIL',
            'VERTEX_GREASE_PENCIL',
            'EDIT', 
            'OBJECT', 
            'SCULPT'
        }
    
    def draw(self, context):
        draw_coloraide_panels(self, context)

class CLIP_PT_coloraide(Panel):
    bl_label = "Coloraide 1.5.0"
    bl_idname = "CLIP_PT_coloraide"
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Coloraide"
    
    def draw(self, context):
        draw_coloraide_panels(self, context)