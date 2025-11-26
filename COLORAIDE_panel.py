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
    """Draw all Coloraide panels in the specified order"""
    wm = context.window_manager
    if not hasattr(wm, 'coloraide_display'):
        return
    
    layout = self.layout
    
    # 1. Draw color wheel
    draw_wheel_panel(layout, context)
    
    # 2. Draw color dynamics (native Blender color jitter)
    draw_dynamics_panel(layout, context)

    # 3. Draw core color picker
    draw_picker_panel(layout, context)
    
    # 4. Color spaces box
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
    
    
    # 5. Draw color history
    draw_history_panel(layout, context)
    
    # 6. Draw palettes
    draw_palette_panel(layout, context)

    # 7. Draw object colors
    draw_object_colors_panel(layout, context)

class IMAGE_PT_coloraide(Panel):
    bl_label = "Coloraide 1.5.0"
    bl_idname = "IMAGE_PT_coloraide"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Coloraide"  # ← CHANGED FROM "Color"
    
    def draw(self, context):
        draw_coloraide_panels(self, context)

class VIEW3D_PT_coloraide(Panel):
    bl_label = "Coloraide 1.5.0"
    bl_idname = "VIEW3D_PT_coloraide"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Coloraide"  # ← CHANGED FROM "Color"
    
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
    bl_category = "Coloraide"  # ← CHANGED FROM "Color"
    
    def draw(self, context):
        draw_coloraide_panels(self, context)