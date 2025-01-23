# PALETTE_OT.py
import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from ..COLORAIDE_sync import sync_all, is_updating

class PALETTE_OT_add_color(Operator):
    bl_idname = "palette.add_color"
    bl_label = "Add to Palette"
    bl_options = {'REGISTER', 'UNDO'}
    
    color: FloatVectorProperty(
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0
    )
    
    def execute(self, context):
        ts = context.tool_settings
        paint_settings = ts.gpencil_paint if context.mode == 'PAINT_GPENCIL' else ts.image_paint
        
        if paint_settings and paint_settings.palette:
            color = paint_settings.palette.colors.new()
            color.color = self.color
            return {'FINISHED'}
        return {'CANCELLED'}

class PALETTE_OT_select_color(Operator):
    bl_idname = "palette.select_color" 
    bl_label = "Select Color"
    bl_options = {'REGISTER', 'UNDO'}
    
    color: FloatVectorProperty(
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0
    )
    
    def execute(self, context):
        if not is_updating():
            sync_all(context, 'palette', self.color)
        return {'FINISHED'}