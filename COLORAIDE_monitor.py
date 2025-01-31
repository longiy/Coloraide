# COLORAIDE_monitor.py
import bpy
from bpy.types import Operator
from .COLORAIDE_brush_sync import sync_picker_from_brush, is_brush_updating

class COLOR_OT_monitor(Operator):
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    old_gp_color = None
    old_image_color = None
    
    def check_color_change(self, context, paint_settings, old_color):
        """Check for color changes in paint settings"""
        if not paint_settings or not paint_settings.brush:
            return None, old_color
                
        curr_color = None
        ts = context.tool_settings
            
        if ts.unified_paint_settings.use_unified_color:
            curr_color = tuple(ts.unified_paint_settings.color)
        else:
            curr_color = tuple(paint_settings.brush.color)
                
        if curr_color != old_color:
            return curr_color, curr_color
                
        return None, old_color

    def modal(self, context, event):
        try:
            ts = context.tool_settings
            color_changed = False
            update_color = None
            
            # Monitor Grease Pencil colors
            if hasattr(ts, 'gpencil_paint'):
                new_color, self.old_gp_color = self.check_color_change(
                    context, 
                    ts.gpencil_paint,
                    self.old_gp_color
                )
                if new_color:
                    color_changed = True
                    update_color = new_color
            
            # Monitor Image Paint colors
            if hasattr(ts, 'image_paint'):
                new_color, self.old_image_color = self.check_color_change(
                    context, 
                    ts.image_paint,
                    self.old_image_color
                )
                if new_color:
                    color_changed = True
                    update_color = new_color
                    
            # Monitor Vertex Paint colors
            if hasattr(ts, 'vertex_paint'):
                new_color, self.old_vertex_color = self.check_color_change(
                    context,
                    ts.vertex_paint,
                    self.old_vertex_color
                )
                if new_color:
                    color_changed = True
                    update_color = new_color
            
            # Update Coloraide if any color changed
            if color_changed and update_color and not is_brush_updating():
                sync_picker_from_brush(context, update_color)
                    
        except Exception as e:
            print(f"Color monitor error: {e}")
                
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        # Initialize tracking colors
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint and ts.gpencil_paint.brush:
            self.old_gp_color = tuple(ts.gpencil_paint.brush.color)
                
        if hasattr(ts, 'image_paint') and ts.image_paint and ts.image_paint.brush:
            self.old_image_color = tuple(ts.image_paint.brush.color)
            
        if hasattr(ts, 'vertex_paint') and ts.vertex_paint and ts.vertex_paint.brush:
            self.old_vertex_color = tuple(ts.vertex_paint.brush.color)
                
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}