"""Override Blender's built-in palette color selection."""
import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from ..COLORAIDE_sync import sync_all

class WM_OT_context_set_id(Operator):
    bl_idname = "wm.context_set_id"
    bl_label = "Set ID"
    bl_options = {'INTERNAL', 'UNDO'}
    
    _original = None
    
    # Match original operator properties
    data_path: StringProperty(name="Context Attributes", description="RNA context string")
    value: StringProperty(name="Value", description="Assignment value")
    relative: BoolProperty(name="Relative", description="Apply relative to current value (delta)")
    
    @staticmethod
    def _find_original():
        if WM_OT_context_set_id._original is None:
            # Get original from add-ons first
            for addon in bpy.context.preferences.addons:
                if hasattr(addon.module, 'WM_OT_context_set_id'):
                    WM_OT_context_set_id._original = addon.module.WM_OT_context_set_id
                    break
            # Fallback to built-in
            if WM_OT_context_set_id._original is None:
                for cls in bpy.types.Operator.__subclasses__():
                    if cls.bl_idname == 'wm.context_set_id' and cls != WM_OT_context_set_id:
                        WM_OT_context_set_id._original = cls
                        break
        return WM_OT_context_set_id._original

    @classmethod
    def poll(cls, context):
        original = cls._find_original()
        if not original:
            return False
        return original.poll(context) if hasattr(original, 'poll') else True

    def execute(self, context):
        original = self._find_original()
        if not original:
            return {'CANCELLED'}
            
        # Create instance of original operator
        orig_op = original()
        orig_op.data_path = self.data_path
        orig_op.value = self.value
        orig_op.relative = self.relative
        
        # Execute original
        result = orig_op.execute(context)
        
        # If successful and it's a palette color selection
        if 'FINISHED' in result and 'palette.colors.active' in self.data_path:
            ts = context.tool_settings
            paint_settings = ts.gpencil_paint if context.mode == 'PAINT_GPENCIL' else ts.image_paint
            
            if paint_settings and paint_settings.palette:
                active_color = paint_settings.palette.colors.active
                if active_color:
                    # Direct sync without monitor
                    sync_all(context, 'palette', active_color.color)
                    
                    # Add to history
                    if hasattr(context.window_manager, 'coloraide_history'):
                        context.window_manager.coloraide_history.add_color(active_color.color)
        
        return result