# COLORAIDE_monitor.py
import bpy
from bpy.types import Operator
from .COLORAIDE_brush_sync import sync_picker_from_brush, is_brush_updating

class COLOR_OT_monitor(Operator):
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    old_color = None
    last_mode = None
    
    def modal(self, context, event):
        try:
            ts = context.tool_settings
            curr_color = None
            
            # Reset old_color if mode changed to force update
            if self.last_mode != context.mode:
                self.old_color = None
                self.last_mode = context.mode
            
            # Handle Grease Pencil vertex paint mode
            if context.mode == 'PAINT_GREASE_PENCIL':
                if hasattr(ts, 'gpencil_vertex_paint') and ts.gpencil_vertex_paint and ts.gpencil_vertex_paint.brush:
                    curr_color = tuple(ts.gpencil_vertex_paint.brush.color)
            # Handle texture paint mode
            elif hasattr(ts, 'image_paint') and ts.image_paint and ts.image_paint.brush:
                curr_color = tuple(ts.image_paint.brush.color)
            
            # If color changed, update coloraide
            if curr_color != self.old_color and curr_color is not None:
                if not is_brush_updating():
                    sync_picker_from_brush(context, curr_color)
                self.old_color = curr_color
                
        except Exception as e:
            print(f"Color monitor error: {e}")
            
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.last_mode = context.mode
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}