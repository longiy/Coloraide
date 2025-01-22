"""
Operators for palette management and color operations.
"""

import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty

class PALETTE_OT_add_color(Operator):
    """Add current color to active palette"""
    bl_idname = "palette.add_color"
    bl_label = "Add to Palette"
    bl_description = "Add current color to active palette"
    bl_options = {'REGISTER', 'UNDO'}
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
    )
    
    @classmethod
    def poll(cls, context):
        ts = context.tool_settings
        if context.mode == 'PAINT_GPENCIL':
            return ts.gpencil_paint.palette is not None
        else:
            return ts.image_paint.palette is not None
    
    def execute(self, context):
        # Get active paint settings
        ts = context.tool_settings
        if context.mode == 'PAINT_GPENCIL':
            paint_settings = ts.gpencil_paint
        else:
            paint_settings = ts.image_paint
            
        # Add color to palette
        if paint_settings and paint_settings.palette:
            color = paint_settings.palette.colors.new()
            color.color = self.color
            color.weight = 1.0  # Default weight
            return {'FINISHED'}
            
        return {'CANCELLED'}

class PALETTE_OT_select_color(Operator):
    """Select color from palette and update current color"""
    bl_idname = "palette.select_color"
    bl_label = "Select Palette Color"
    bl_description = "Use this color for painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
    )
    
    def execute(self, context):
        # Update preview color in palette properties
        palette_props = context.window_manager.coloraide_palette
        palette_props.suppress_updates = True
        palette_props.preview_color = self.color
        palette_props.suppress_updates = False
        
        # Trigger color update
        palette_props.update_preview_color(context)
        return {'FINISHED'}

class PALETTE_OT_remove_color(Operator):
    """Remove selected color from palette"""
    bl_idname = "palette.remove_color"
    bl_label = "Remove Color"
    bl_description = "Remove selected color from palette"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        ts = context.tool_settings
        if context.mode == 'PAINT_GPENCIL':
            palette = ts.gpencil_paint.palette
        else:
            palette = ts.image_paint.palette
        return palette and palette.colors.active
    
    def execute(self, context):
        # Get active paint settings and palette
        ts = context.tool_settings
        if context.mode == 'PAINT_GPENCIL':
            palette = ts.gpencil_paint.palette
        else:
            palette = ts.image_paint.palette
            
        if palette and palette.colors.active:
            # Remove active color
            palette.colors.remove(palette.colors.active)
            return {'FINISHED'}
            
        return {'CANCELLED'}

def register():
    bpy.utils.register_class(PALETTE_OT_add_color)
    bpy.utils.register_class(PALETTE_OT_select_color)
    bpy.utils.register_class(PALETTE_OT_remove_color)

def unregister():
    bpy.utils.unregister_class(PALETTE_OT_remove_color)
    bpy.utils.unregister_class(PALETTE_OT_select_color)
    bpy.utils.unregister_class(PALETTE_OT_add_color)