"""
Copyright (C) 2024 Spencer Magnusson & longiy
semagnum@gmail.com
longiyart@gmail.com
"""

import bpy
from bpy.types import Panel, Operator
from bpy.props import BoolProperty
from bpy.props import FloatVectorProperty
from ..operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from ..operators.IMAGE_OT_screen_rect import IMAGE_OT_screen_rect
from ..utils.color_conversions import rgb_to_lab, lab_to_rgb

panel_title = 'Coloraide'

class COLOR_OT_pick_from_history(Operator):
    bl_idname = "color.pick_from_history"
    bl_label = "Pick Color From History"
    bl_description = "Set the current color from history"
    bl_options = {'REGISTER', 'UNDO'}
    
    color: FloatVectorProperty(
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0,
        max=1.0
    )
    
    def execute(self, context):
        wm = context.window_manager
        wm.picker_mean = self.color
        wm.picker_current = self.color
        # Update the brush colors
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = self.color
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = self.color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = self.color
        return {'FINISHED'}

class COLOR_OT_adjust_history_size(Operator):
    bl_idname = "color.adjust_history_size"
    bl_label = "Adjust History Size"
    bl_options = {'INTERNAL'}
    
    increase: BoolProperty()
    
    @classmethod
    def description(cls, context, properties):
        if properties.increase:
            return "Add one more color slot (Maximum 30)"
        else:
            return "Remove one color slot (Minimum 5)"
    
    def execute(self, context):
        wm = context.window_manager
        if self.increase:
            wm.history_size = min(wm.history_size + 1, 30)
        else:
            wm.history_size = max(wm.history_size - 1, 5)
        return {'FINISHED'}

def update_lab(self, context):
    """Update handler for LAB slider changes"""
    global _updating_lab, _updating_rgb, _updating_picker
    if _updating_rgb or _updating_picker:
        return
    
    _updating_lab = True
    try:
        wm = context.window_manager
        
        # Get and round LAB values
        lab = (round(self.lab_l), round(self.lab_a), round(self.lab_b))
        
        # Convert to RGB through LAB values
        rgb_float = lab_to_rgb(lab)
        rgb_bytes = rgb_float_to_byte(rgb_float)
        
        # Update RGB values
        if tuple(wm.picker_mean) != rgb_float:  # Only update if different
            wm["picker_mean"] = rgb_float
        wm["picker_current"] = rgb_float
        wm["picker_mean_r"] = rgb_bytes[0]
        wm["picker_mean_g"] = rgb_bytes[1]
        wm["picker_mean_b"] = rgb_bytes[2]
        
        # Update brush colors
        update_all_colors(rgb_float, context)
    finally:
        _updating_lab = False

def update_rgb_byte(self, context):
    """Update handler for RGB byte value changes (0-255 range)"""
    global _updating_lab, _updating_rgb, _updating_picker
    if _updating_lab or _updating_picker:
        return
        
    _updating_rgb = True
    try:
        wm = context.window_manager
        
        # Get RGB bytes and convert to float
        rgb_bytes = (
            wm.picker_mean_r,
            wm.picker_mean_g,
            wm.picker_mean_b
        )
        rgb_float = rgb_byte_to_float(rgb_bytes)
        
        # Convert to LAB and back to ensure consistency
        lab = rgb_to_lab(rgb_float)
        lab = (round(lab[0]), round(lab[1]), round(lab[2]))
        
        # Update LAB values
        wm["lab_l"] = lab[0]
        wm["lab_a"] = lab[1]
        wm["lab_b"] = lab[2]
        
        # Convert back to RGB through LAB
        rgb_float = lab_to_rgb(lab)
        
        # Update RGB float values
        if tuple(wm.picker_mean) != rgb_float:  # Only update if different
            wm["picker_mean"] = rgb_float
        wm["picker_current"] = rgb_float
        
        # Update brush colors
        update_all_colors(rgb_float, context)
    finally:
        _updating_rgb = False

def draw_panel(layout, context):
    wm = context.window_manager
        
    # Add color wheel with dynamic scaling
    col = layout.column()
    col.scale_y = wm.wheel_scale
    col.template_color_picker(wm, "wheel_color", value_slider=True, lock_luminosity=False)
    
    # Add wheel scale slider
    layout.prop(wm, "wheel_scale", slider=True)
    
    # Original color display row
    row = layout.row(align=True) 
    row.scale_y = 2.0
    row.prop(wm, 'picker_mean', text='')
    row.prop(wm, 'picker_current', text='')
    
    # Add hex code display
    row = layout.row(align=True)
    split = row.split(factor=0.2)
    split.label(text="Hex:")
    hex_field = split.prop(wm, "hex_color", text="")
    
    # Color history section
    header_row = layout.row(align=True)
    header_row.label(text=f"Color History {wm.history_size}")
    
    size_row = header_row.row(align=True)
    size_row.scale_x = 0.5
    minus = size_row.operator("color.adjust_history_size", text="-")
    minus.increase = False
    plus = size_row.operator("color.adjust_history_size", text="+")
    plus.increase = True

    colors_per_row = 7
    history = list(wm.picker_history)
    num_rows = (wm.history_size + colors_per_row - 1) // colors_per_row
    
    for row_idx in range(num_rows):
        history_row = layout.row(align=True)
        history_row.scale_y = 1.0
        
        start_idx = row_idx * colors_per_row
        end_idx = min(start_idx + colors_per_row, wm.history_size)
        
        row_colors = history[start_idx:end_idx]
        for item in row_colors:
            sub = history_row.row(align=True)
            sub.scale_x = 1.0
            sub.prop(item, "color", text="", event=True)
        
        empty_spots = min(colors_per_row, end_idx - start_idx) - len(row_colors)
        if empty_spots > 0:
            for _ in range(empty_spots):
                sub = history_row.row(align=True)
                sub.scale_x = 1.0
                sub.enabled = False
                sub.label(text="")
    
    # row = layout.row(align=True) 
    # row.prop(wm, 'picker_min', text='Min')
    # row.prop(wm, 'picker_max', text='Max')
    
    # RGB sliders box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm, "show_rgb_sliders", text="RGB", icon='TRIA_DOWN' if wm.show_rgb_sliders else 'TRIA_RIGHT', emboss=False)
    
    if wm.show_rgb_sliders:
        col = box.column(align=True)
        split = col.split(factor=0.1)
        split.label(text="R:")
        split.prop(wm, 'picker_mean_r', text="", slider=True)
        
        split = col.split(factor=0.1)
        split.label(text="G:")
        split.prop(wm, 'picker_mean_g', text="", slider=True)
        
        split = col.split(factor=0.1)
        split.label(text="B:")
        split.prop(wm, 'picker_mean_b', text="", slider=True)
    
    # LAB sliders box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm, "show_lab_sliders", text="LAB", icon='TRIA_DOWN' if wm.show_lab_sliders else 'TRIA_RIGHT', emboss=False)
    
    if wm.show_lab_sliders:
        col = box.column(align=True)
        split = col.split(factor=0.1)
        split.label(text="L:")
        split.prop(wm, "lab_l", text="", slider=True)
        
        split = col.split(factor=0.1)
        split.label(text="a:")
        split.prop(wm, "lab_a", text="", slider=True)
        
        split = col.split(factor=0.1)
        split.label(text="b:")
        split.prop(wm, "lab_b", text="", slider=True)
    
    
    row = layout.row(align=True) 
    row.operator('image.screen_picker', text='1x1', icon='EYEDROPPER').sqrt_length = 1
    row.operator('image.screen_picker', text='5x5', icon='EYEDROPPER').sqrt_length = 5
    
    row = layout.row(align=True)
    split = row.split(factor=1)
    split.prop(wm, 'custom_size', slider=True)
    row = layout.row(align=True)
    row.operator('image.screen_picker', text=str(wm.custom_size) + 'x' + str(wm.custom_size), icon='EYEDROPPER').sqrt_length = wm.custom_size

    # layout.separator()
    # layout.operator(IMAGE_OT_screen_rect.bl_idname, text='Rect Color Picker', icon='SELECT_SET')

class IMAGE_PT_color_picker(Panel):
    bl_label = "Coloraide"
    bl_idname = 'IMAGE_PT_color_picker'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Color"

    def draw(self, context):
        draw_panel(self.layout, context)

class VIEW_PT_color_picker(Panel):
    bl_label = "Coloraide"
    bl_idname = 'VIEW_PT_color_picker'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Color"

    def draw(self, context):
        draw_panel(self.layout, context)

class CLIP_PT_color_picker(Panel):
    bl_label = "Coloraide"
    bl_idname = 'CLIP_PT_color_picker'
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Color"

    def draw(self, context):
        draw_panel(self.layout, context)

__all__ = [
    'IMAGE_PT_color_picker',
    'VIEW_PT_color_picker',
    'CLIP_PT_color_picker',
    'COLOR_OT_adjust_history_size'
]