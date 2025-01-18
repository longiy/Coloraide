"""
Copyright (C) 2024 Spencer Magnusson & longiy
semagnum@gmail.com
longiyart@gmail.com
"""

import bpy
from bpy.types import Panel, Operator
from bpy.props import BoolProperty, FloatVectorProperty



def draw_palette_section(layout, context):
    """Draw the native palette section of the panel"""
    box = layout.box()
    row = box.row()
    row.prop(context.window_manager.coloraide_display, "show_palettes", 
        text="Color Palettes", 
        icon='TRIA_DOWN' if context.window_manager.coloraide_display.show_palettes else 'TRIA_RIGHT',
        emboss=False
    )
    
    if context.window_manager.coloraide_display.show_palettes:
        ts = context.tool_settings
        
        # Determine which paint mode we're in and get the corresponding palette
        if context.mode == 'PAINT_GPENCIL':
            paint_settings = ts.gpencil_paint
        else:
            paint_settings = ts.image_paint
            
        # Palette selector with new button
        row = box.row(align=True)
        row.template_ID(paint_settings, "palette", new="palette.new")
        
        if paint_settings and paint_settings.palette:
            # Control buttons in their own column
            controls_col = box.column()
            row = controls_col.row(align=True)
            row.alignment = 'LEFT'
            row.operator("palette.colors_add", text="", icon='ADD')
            row.operator("palette.colors_remove", text="", icon='REMOVE')
            up_op = row.operator("palette.colors_move", text="", icon='TRIA_UP')
            if up_op:
                up_op.direction = 'UP'
            down_op = row.operator("palette.colors_move", text="", icon='TRIA_DOWN')
            if down_op:
                down_op.direction = 'DOWN'
            row.operator("palette.colors_filter", text="", icon='FILTER')
            
            # Separate boxed area for palette swatches
            palette_box = box.column()
            palette_box.template_palette(paint_settings, "palette", color=True)


class PALETTE_OT_select_color(bpy.types.Operator):
    """Select color from palette and update picker"""
    bl_idname = "palette.select_color"
    bl_label = "Select Palette Color"
    bl_description = "Use this color in the color picker"
    bl_options = {'REGISTER', 'UNDO'}
    
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        min=0.0,
        max=1.0,
        size=3,
        default=(0.0, 0.0, 0.0)
    )
    
    def execute(self, context):
        context.window_manager.coloraide_picker.mean = self.color
        return {'FINISHED'}

# Update the operator class
class PAINT_OT_add_palette_color(bpy.types.Operator):
    """Add current color to active palette"""
    bl_idname = "paint.add_palette_color"
    bl_label = "Add Color to Palette"
    bl_description = "Add current color to active palette"
    bl_options = {'REGISTER', 'UNDO'}
    
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        min=0.0,
        max=1.0,
        size=3,
        default=(0.0, 0.0, 0.0)
    )
    
    @classmethod
    def poll(cls, context):
        ts = context.tool_settings
        if context.mode == 'PAINT_GPENCIL':
            return (ts.gpencil_paint.palette is not None and
                    hasattr(context.window_manager, 'coloraide_picker'))
        else:
            return (ts.image_paint.palette is not None and
                    hasattr(context.window_manager, 'coloraide_picker'))
    
    def execute(self, context):
        ts = context.tool_settings
        if context.mode == 'PAINT_GPENCIL':
            palette = ts.gpencil_paint.palette
        else:
            palette = ts.image_paint.palette
            
        if palette:
            color = palette.colors.new()
            color.color = self.color
            color.weight = 1.0
            return {'FINISHED'}
        return {'CANCELLED'}


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

      # Normal picker section
    box = layout.box()
    row = box.row()
    # Use operator instead of direct property
    op = row.operator("brush.normal_color_picker", 
        text="Normal Color Sampler",
        icon='NORMALS_VERTEX' if wm.normal_picker.enabled else 'NORMALS_VERTEX_FACE',
        depress=wm.normal_picker.enabled
    )
    
    if wm.normal_picker.enabled:
        sub = box.row()
        sub.prop(wm.normal_picker, "space", text="Space")


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
    
     # Add palette section before quick pick size
    draw_palette_section(layout, context)
    
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
    bl_label = "Coloraide 1.2.0"
    bl_idname = 'IMAGE_PT_color_picker'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Color"

    def draw(self, context):
        draw_panel(self.layout, context)

class VIEW_PT_color_picker(Panel):
    bl_label = "Coloraide 1.2.0"
    bl_idname = 'VIEW_PT_color_picker'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Color"

    def draw(self, context):
        draw_panel(self.layout, context)

class CLIP_PT_color_picker(Panel):
    bl_label = "Coloraide 1.2.0"
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
    'COLOR_OT_adjust_history_size',
    'PAINT_OT_add_palette_color',
    'PALETTE_OT_select_color',
]