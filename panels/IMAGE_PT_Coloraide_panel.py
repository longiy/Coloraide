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
    # Convert LAB to RGB and update picker_mean
    lab = (self.lab_l, self.lab_a, self.lab_b)
    rgb = lab_to_rgb(lab)
    
    wm = context.window_manager
    wm.picker_mean = rgb
    wm.picker_current = rgb
    
    # Update brush colors
    ts = context.tool_settings
    if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
        ts.gpencil_paint.brush.color = rgb
    if hasattr(ts, 'image_paint') and ts.image_paint.brush:
        ts.image_paint.brush.color = rgb
        if ts.unified_paint_settings.use_unified_color:
            ts.unified_paint_settings.color = rgb

def update_rgb(self, context):
    # Convert RGB to LAB and update LAB properties
    rgb = self.picker_mean
    lab = rgb_to_lab(rgb)
    
    # Update LAB properties without triggering their update callbacks
    wm = context.window_manager
    wm["lab_l"] = lab[0]
    wm["lab_a"] = lab[1]
    wm["lab_b"] = lab[2]

def draw_panel(layout, context):
    wm = context.window_manager
    row = layout.row(align=True) 

    row.scale_y = 2.0
    row.prop(wm, 'picker_mean', text='')
    row.prop(wm, 'picker_current', text='')
    
    # RGB sliders for fine-tuning mean color
    box = layout.box()
    col = box.column(align=True)
    col.label(text="RGB Adjust")
    
    # Split the color into individual RGB components with visual sliders
    split = col.split(factor=0.1)
    split.label(text="R:")
    split.prop(wm, 'picker_mean', text="", index=0, slider=True)
    
    split = col.split(factor=0.1)
    split.label(text="G:")
    split.prop(wm, 'picker_mean', text="", index=1, slider=True)
    
    split = col.split(factor=0.1)
    split.label(text="B:")
    split.prop(wm, 'picker_mean', text="", index=2, slider=True)
    
     # LAB sliders - new addition
    box = layout.box()
    col = box.column(align=True)
    col.label(text="LAB")
    
    split = col.split(factor=0.1)
    split.label(text="L:")
    split.prop(wm, "lab_l", text="", slider=True)
    
    split = col.split(factor=0.1)
    split.label(text="a:")
    split.prop(wm, "lab_a", text="", slider=True)
    
    split = col.split(factor=0.1)
    split.label(text="b:")
    split.prop(wm, "lab_b", text="", slider=True)
    
    header_row = layout.row(align=True)
    header_row.label(text=f"Color History {wm.history_size}")
    
    size_row = header_row.row(align=True)
    size_row.scale_x = 0.5
    minus = size_row.operator("color.adjust_history_size", text="-")
    minus.increase = False
    plus = size_row.operator("color.adjust_history_size", text="+")
    plus.increase = True

    colors_per_row = 5
    history = list(wm.picker_history)
    num_rows = (wm.history_size + colors_per_row - 1) // colors_per_row
    
    for row_idx in range(num_rows):
        history_row = layout.row(align=True)
        history_row.scale_y = 1.0
        
        start_idx = row_idx * colors_per_row
        end_idx = min(start_idx + colors_per_row, wm.history_size)
        
        # Add existing colors
        row_colors = history[start_idx:end_idx]
        for item in row_colors:
            sub = history_row.row(align=True)
            sub.scale_x = 1.0
            sub.prop(item, "color", text="", event=True)
        
        # Fill empty spots with blank labels instead of operators
        empty_spots = min(colors_per_row, end_idx - start_idx) - len(row_colors)
        if empty_spots > 0:
            for _ in range(empty_spots):
                sub = history_row.row(align=True)
                sub.scale_x = 1.0
                sub.enabled = False
                sub.label(text="")  # Just use a blank label instead of an operator
    
    row = layout.row(align=True) 
    row.prop(wm, 'picker_min', text='Min')
    row.prop(wm, 'picker_max', text='Max')
    
    row = layout.row(align=True) 
    row.operator(IMAGE_OT_screen_picker.bl_idname, text='1x1', icon='EYEDROPPER').sqrt_length = 1
    row.operator(IMAGE_OT_screen_picker.bl_idname, text='5x5', icon='EYEDROPPER').sqrt_length = 5
    
    row = layout.row(align=True)
    split = row.split(factor=1)
    split.prop(wm, 'custom_size', slider=True)

    layout.separator()
    layout.operator(IMAGE_OT_screen_rect.bl_idname, text='Rect Color Picker', icon='SELECT_SET')

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