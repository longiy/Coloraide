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
        paint_settings = ts.gpencil_paint if context.mode == 'PAINT_GPENCIL' else ts.image_paint
        
        if paint_settings and paint_settings.palette:
            new_color = paint_settings.palette.colors.new()
            new_color.color = self.color
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
        wm = context.window_manager
        ts = context.tool_settings
        
        # Update brush color directly first
        if context.mode == 'VERTEX_GPENCIL':
            if ts.gpencil_vertex_paint and ts.gpencil_vertex_paint.brush:
                ts.gpencil_vertex_paint.brush.color = self.color
        elif context.mode == 'PAINT_GPENCIL':
            if ts.gpencil_paint and ts.gpencil_paint.brush:
                ts.gpencil_paint.brush.color = self.color
        elif ts.image_paint and ts.image_paint.brush:
            ts.image_paint.brush.color = self.color
        
        # Update picker
        wm.coloraide_picker.suppress_updates = True
        wm.coloraide_picker.mean = self.color
        wm.coloraide_picker.current = self.color
        wm.coloraide_picker.suppress_updates = False
        
        # Then do full sync
        sync_all(context, 'picker', self.color)
        return {'FINISHED'}

class PALETTE_OT_remove_color(Operator):
    bl_idname = "palette.remove_color"
    bl_label = "Remove Color"
    bl_description = "Remove selected color from palette"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        ts = context.tool_settings
        paint_settings = ts.gpencil_paint if context.mode == 'PAINT_GPENCIL' else ts.image_paint
        return (paint_settings and paint_settings.palette 
                and paint_settings.palette.colors.active)
    
    def execute(self, context):
        ts = context.tool_settings
        paint_settings = ts.gpencil_paint if context.mode == 'PAINT_GPENCIL' else ts.image_paint
        
        if paint_settings and paint_settings.palette:
            paint_settings.palette.colors.remove(paint_settings.palette.colors.active)
            return {'FINISHED'}
        return {'CANCELLED'}