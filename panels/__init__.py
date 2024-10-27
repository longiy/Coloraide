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

from ..operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from ..operators.IMAGE_OT_screen_rect import IMAGE_OT_screen_rect

panel_title = 'Color Picker Pro'


def draw_panel(layout, context):
    wm = context.window_manager
    row = layout.row(align=True) 

    row.scale_y = 2.0
    row.prop(wm, 'picker_mean', text='')
    row.prop(wm, 'picker_current', text='')
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




class IMAGE_PT_color_picker(bpy.types.Panel):
    bl_label = panel_title
    bl_idname = 'IMAGE_PT_color_picker'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        draw_panel(self.layout, context)


class VIEW_PT_color_picker(bpy.types.Panel):
    bl_label = panel_title
    bl_idname = 'VIEW_PT_color_picker'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        draw_panel(self.layout, context)


class CLIP_PT_color_picker(bpy.types.Panel):
    bl_label = panel_title
    bl_idname = 'CLIP_PT_color_picker'
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        draw_panel(self.layout, context)\


