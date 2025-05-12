import bpy
from bpy.props import FloatVectorProperty
from bpy.types import Operator
from ..COLORAIDE_sync import sync_all

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
        paint_settings = None
        
        # Get correct paint settings based on mode
        if context.mode == 'PAINT_GPENCIL':
            paint_settings = ts.gpencil_paint
        elif context.mode == 'PAINT_VERTEX':
            paint_settings = ts.vertex_paint
        elif context.mode == 'VERTEX_GPENCIL':
            paint_settings = ts.gpencil_vertex_paint
        else:
            paint_settings = ts.image_paint
            
        if paint_settings and paint_settings.palette:
            new_color = paint_settings.palette.colors.new()
            new_color.color = self.color
            # Make the new color active
            paint_settings.palette.colors.active = new_color
            # Sync to Coloraide
            sync_all(context, 'palette', self.color)
            return {'FINISHED'}
        return {'CANCELLED'}

class PALETTE_OT_remove_color(Operator):
    bl_idname = "palette.remove_color"
    bl_label = "Remove Color"
    bl_description = "Remove selected color from palette"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        ts = context.tool_settings
        paint_settings = None
        if context.mode == 'PAINT_GPENCIL':
            paint_settings = ts.gpencil_paint
        elif context.mode == 'PAINT_VERTEX':
            paint_settings = ts.vertex_paint
        elif context.mode == 'VERTEX_GPENCIL':
            paint_settings = ts.gpencil_vertex_paint
        else:
            paint_settings = ts.image_paint
            
        return (paint_settings and paint_settings.palette 
                and paint_settings.palette.colors.active)
    
    def execute(self, context):
        ts = context.tool_settings
        paint_settings = None
        
        # Get correct paint settings based on mode
        if context.mode == 'PAINT_GPENCIL':
            paint_settings = ts.gpencil_paint
        elif context.mode == 'PAINT_VERTEX':
            paint_settings = ts.vertex_paint
        elif context.mode == 'VERTEX_GPENCIL':
            paint_settings = ts.gpencil_vertex_paint
        else:
            paint_settings = ts.image_paint
        
        if paint_settings and paint_settings.palette:
            paint_settings.palette.colors.remove(paint_settings.palette.colors.active)
            return {'FINISHED'}
        return {'CANCELLED'}