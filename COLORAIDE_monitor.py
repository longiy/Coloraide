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
    old_vertex_color = None
    old_palette_color = None
    
    def check_color_change(self, context, paint_settings, old_color):
        """Check for color changes in paint settings"""
        if not paint_settings:
            return None, old_color
            
        curr_color = check_brush_color(context, paint_settings)
        if not curr_color:
            return None, old_color
            
        if curr_color != old_color:
            return curr_color, curr_color
            
        return None, old_color
    
    def modal(self, context, event):
        try:
            ts = context.tool_settings
            color_changed = False
            update_color = None
            
            # Get current paint settings based on mode
            paint_settings = None
            if context.mode == 'PAINT_GPENCIL':
                paint_settings = ts.gpencil_paint
                old_color = self.old_gp_color
            elif context.mode == 'PAINT_VERTEX':
                paint_settings = ts.vertex_paint
                old_color = self.old_vertex_color
            else:
                paint_settings = ts.image_paint
                old_color = self.old_image_color

            # Check for color changes including palette
            if paint_settings:
                # Check active palette color
                if paint_settings.palette and paint_settings.palette.colors.active:
                    curr_palette_color = tuple(paint_settings.palette.colors.active.color)
                    if curr_palette_color != self.old_palette_color:
                        color_changed = True
                        update_color = curr_palette_color
                        self.old_palette_color = curr_palette_color
                
                # Check brush color
                if not color_changed:  # Only check if palette didn't change
                    new_color, old_color = self.check_color_change(
                        context, 
                        paint_settings,
                        old_color
                    )
                    if new_color:
                        color_changed = True
                        update_color = new_color
            
            # Store updated old color based on mode
            if context.mode == 'PAINT_GPENCIL':
                self.old_gp_color = old_color
            elif context.mode == 'PAINT_VERTEX':
                self.old_vertex_color = old_color
            else:
                self.old_image_color = old_color
            
            # Update Coloraide if any color changed
            if color_changed and update_color and not is_brush_updating():
                sync_picker_from_brush(context, update_color)
                
        except Exception as e:
            print(f"Color monitor error: {e}")
            
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        # Initialize tracking colors
        ts = context.tool_settings
        
        # Initialize colors for all paint modes
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint and ts.gpencil_paint.brush:
            self.old_gp_color = tuple(ts.gpencil_paint.brush.color)
            
        if hasattr(ts, 'image_paint') and ts.image_paint and ts.image_paint.brush:
            self.old_image_color = tuple(ts.image_paint.brush.color)
            
        if hasattr(ts, 'vertex_paint') and ts.vertex_paint and ts.vertex_paint.brush:
            self.old_vertex_color = tuple(ts.vertex_paint.brush.color)
        
        # Initialize palette color tracking
        paint_settings = None
        if context.mode == 'PAINT_GPENCIL':
            paint_settings = ts.gpencil_paint
        elif context.mode == 'PAINT_VERTEX':
            paint_settings = ts.vertex_paint
        else:
            paint_settings = ts.image_paint
            
        if paint_settings and paint_settings.palette and paint_settings.palette.colors.active:
            self.old_palette_color = tuple(paint_settings.palette.colors.active.color)
            
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}