"""
Copyright (C) 2023 Spencer Magnusson
semagnum@gmail.com
Created by Spencer Magnusson
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import bpy
from bpy.types import Panel, Operator
from bpy.props import FloatVectorProperty
from ..operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from ..operators.IMAGE_OT_screen_rect import IMAGE_OT_screen_rect

panel_title = 'Color Picker Pro'

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

def draw_panel(layout, context):
    wm = context.window_manager
    row = layout.row(align=True) 

    row.scale_y = 2.0
    row.prop(wm, 'picker_mean', text='')
    row.prop(wm, 'picker_current', text='')
    
    # Add color history
    box = layout.box()
    row = box.row(align=True)
    row.label(text="History:")
    history_row = box.row(align=True)
    for item in wm.picker_history:
        op = history_row.operator(COLOR_OT_pick_from_history.bl_idname, text="", icon='COLOR', emboss=False)
        op.color = item.color
        # Create a non-interactive color preview
        sub = history_row.row(align=True)
        sub.scale_x = 0.8
        sub.prop(item, "color", text="")
        sub.enabled = False  # This makes it non-interactive but still visible
    
    row = layout.row(align=True) 
    row.prop(wm, 'picker_min', text='Min')
    row.prop(wm, 'picker_max', text='Max')
    
    row = layout.row(align=True) 

    row.operator(IMAGE_OT_screen_picker.bl_idname, text='3x3', icon='EYEDROPPER').sqrt_length = 3
    row.operator(IMAGE_OT_screen_picker.bl_idname, text='10x10', icon='EYEDROPPER').sqrt_length = 10
        

    row = layout.row(align=True)
    split = row.split(factor=0.85)
    split.prop(wm, 'custom_size', slider=True)

    split.operator(IMAGE_OT_screen_picker.bl_idname, text="", icon='EYEDROPPER').sqrt_length = wm.custom_size
    
    # tile_str = str(wm.custom_size)
    # custom_label = f"{tile_str} x {tile_str}"
    # split.operator(IMAGE_OT_screen_picker.bl_idname, text=custom_label, icon='EYEDROPPER').sqrt_length = wm.custom_size
    

    layout.separator()
    layout.operator(IMAGE_OT_screen_rect.bl_idname, text='Rect Color Picker', icon='SELECT_SET')




class IMAGE_PT_color_picker(Panel):
    bl_label = "Color Picker Pro"
    bl_idname = 'IMAGE_PT_color_picker'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Color"

    def draw(self, context):
        draw_panel(self.layout, context)

class VIEW_PT_color_picker(Panel):
    bl_label = "Color Picker Pro"
    bl_idname = 'VIEW_PT_color_picker'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Color"

    def draw(self, context):
        draw_panel(self.layout, context)

class CLIP_PT_color_picker(Panel):
    bl_label = "Color Picker Pro"
    bl_idname = 'CLIP_PT_color_picker'
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Color"

    def draw(self, context):
        draw_panel(self.layout, context)

    def draw(self, context):
        draw_panel(self.layout, context)\


