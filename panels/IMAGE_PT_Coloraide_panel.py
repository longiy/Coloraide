"""
Copyright (C) 2024 Spencer Magnusson & longiy
semagnum@gmail.com
longiyart@gmail.com
"""

import bpy
from bpy.types import Panel, Operator
from bpy.props import BoolProperty, FloatVectorProperty

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
        wm.coloraide_picker.mean = self.color
        wm.coloraide_picker.current = self.color
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
            return "Add one more color slot (Maximum 40)"
        else:
            return "Remove one color slot (Minimum 8)"
    
    def execute(self, context):
        wm = context.window_manager
        history = wm.color_history.items
        
        if self.increase and wm.color_history.size < 40:
            wm.color_history.size += 1
            if len(history) < wm.color_history.size:
                new_color = history.add()
                new_color.color = (0.0, 0.0, 0.0)
                
        elif not self.increase and wm.color_history.size > 5:
            wm.color_history.size -= 1
            while len(history) > wm.color_history.size:
                history.remove(len(history) - 1)
                
        return {'FINISHED'}

def draw_panel(layout, context):
    wm = context.window_manager
        
    # Add color wheel with dynamic scaling
    col = layout.column()
    col.scale_y = wm.coloraide_wheel.scale
    col.template_color_picker(wm.coloraide_wheel, "color", value_slider=True, lock_luminosity=False)
    
    # Add hex code display and wheel scale
    row = layout.row(align=True)
    split = row.split(factor=0.4)
    hex_field = split.prop(wm.coloraide_picker, "hex_color", text="")
    split.prop(wm.coloraide_wheel, "scale", slider=True)
    
    # Original color display row
    row = layout.row(align=True) 
    row.scale_y = 2.0
    row.prop(wm.coloraide_picker, 'mean', text='')
    row.prop(wm.coloraide_picker, 'current', text='')
    
    # Modified color dynamics section
    row = layout.row(align=True)
    row.prop(wm.color_dynamics, "strength", text="Color Dynamics", slider=True)
    
    # Color history box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_history", 
        text=f"Color History ({wm.color_history.size})", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_history else 'TRIA_RIGHT', 
        emboss=False
    )
    
    if wm.coloraide_display.show_history:
        # Size adjustment row with full width buttons
        size_row = box.row(align=True)
        minus = size_row.operator("color.adjust_history_size", text="-")
        minus.increase = False
        plus = size_row.operator("color.adjust_history_size", text="+")
        plus.increase = True

        box.separator(factor=0.3)

        # Color swatches
        colors_per_row = 8
        history = list(wm.color_history.items)
        
        # Only show swatches up to current history_size
        visible_history = history[:wm.color_history.size]
        num_rows = (len(visible_history) + colors_per_row - 1) // colors_per_row
        
        # Create column for swatch rows
        col = box.column(align=True)
        
        for row_idx in range(num_rows):
            history_row = col.row(align=True)
            
            start_idx = row_idx * colors_per_row
            end_idx = min(start_idx + colors_per_row, len(visible_history))
            
            row_colors = visible_history[start_idx:end_idx]
            for item in row_colors:
                sub = history_row.row(align=True)
                sub.prop(item, "color", text="", event=True)
            
            # Fill empty spots in the last row
            empty_spots = colors_per_row - len(row_colors)
            if empty_spots > 0:
                for _ in range(empty_spots):
                    sub = history_row.row(align=True)
                    sub.enabled = False
                    sub.label(text="")
    
    # RGB sliders box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_rgb_sliders", 
        text="RGB", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_rgb_sliders else 'TRIA_RIGHT', 
        emboss=False
    )
    
    if wm.coloraide_display.show_rgb_sliders:
        col = box.column(align=True)
        split = col.split(factor=0.1)
        split.label(text="R:")
        split.prop(wm.coloraide_picker, 'mean_r', text="", slider=True)
        
        split = col.split(factor=0.1)
        split.label(text="G:")
        split.prop(wm.coloraide_picker, 'mean_g', text="", slider=True)
        
        split = col.split(factor=0.1)
        split.label(text="B:")
        split.prop(wm.coloraide_picker, 'mean_b', text="", slider=True)
    
    # LAB sliders box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_lab_sliders", 
        text="LAB", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_lab_sliders else 'TRIA_RIGHT', 
        emboss=False
    )
    
    if wm.coloraide_display.show_lab_sliders:
        col = box.column(align=True)
        split = col.split(factor=0.1)
        split.label(text="L:")
        split.prop(wm.coloraide_picker, "lab_l", text="", slider=True)
        
        split = col.split(factor=0.1)
        split.label(text="a:")
        split.prop(wm.coloraide_picker, "lab_a", text="", slider=True)
        
        split = col.split(factor=0.1)
        split.label(text="b:")
        split.prop(wm.coloraide_picker, "lab_b", text="", slider=True)
    
    # Quick pick size
    row = layout.row(align=True)
    split = row.split(factor=1)
    split.prop(wm, 'custom_size', slider=True)
    
    # Quick pick operators
    row = layout.row(align=True)
    row.operator('image.screen_picker', 
        text=f"{wm.custom_size}x{wm.custom_size} Quickpick", 
        icon='EYEDROPPER'
    ).sqrt_length = wm.custom_size
    
    row = layout.row(align=True) 
    row.operator('image.screen_picker', text='1x1', icon='EYEDROPPER').sqrt_length = 1
    row.operator('image.screen_picker', text='5x5', icon='EYEDROPPER').sqrt_length = 5

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