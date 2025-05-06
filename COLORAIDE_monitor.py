# COLORAIDE_monitor.py
import bpy
import time
from bpy.types import Operator
from .COLORAIDE_brush_sync import sync_picker_from_brush, is_brush_updating, check_brush_color

class COLOR_OT_monitor(Operator):
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    old_gp_color = None
    old_image_color = None
    old_vertex_color = None
    old_palette_color = None
    is_running = False
    
    @classmethod
    def _timer_function(cls):
        """Function to be called by timer"""
        if not cls.is_running:
            return None
            
        try:
            context = bpy.context
            ts = context.tool_settings
            
            # Get current paint settings based on mode
            paint_settings = None
            if context.mode == 'PAINT_GPENCIL':
                paint_settings = ts.gpencil_paint
                old_color = cls.old_gp_color
            elif context.mode == 'PAINT_VERTEX':
                paint_settings = ts.vertex_paint
                old_color = cls.old_vertex_color
            else:
                paint_settings = ts.image_paint
                old_color = cls.old_image_color

            color_changed = False
            update_color = None
            
            # Check for color changes including palette
            if paint_settings:
                # Check active palette color
                if paint_settings.palette and paint_settings.palette.colors.active:
                    curr_palette_color = tuple(paint_settings.palette.colors.active.color)
                    if curr_palette_color != cls.old_palette_color:
                        color_changed = True
                        update_color = curr_palette_color
                        cls.old_palette_color = curr_palette_color
                
                # Check brush color
                if not color_changed:
                    curr_color = check_brush_color(context, paint_settings)
                    if curr_color and curr_color != old_color:
                        color_changed = True
                        update_color = curr_color
                        # Update stored color
                        if context.mode == 'PAINT_GPENCIL':
                            cls.old_gp_color = curr_color
                        elif context.mode == 'PAINT_VERTEX':
                            cls.old_vertex_color = curr_color
                        else:
                            cls.old_image_color = curr_color
            
            # Update Coloraide if color changed
            if color_changed and update_color and not is_brush_updating():
                sync_picker_from_brush(context, update_color)
                
        except Exception as e:
            print(f"Color monitor error: {e}")
            
        return 0.1  # Check every 0.1 seconds
    
    def invoke(self, context, event):
        # Initialize color tracking
        COLOR_OT_monitor.is_running = False  # Reset state
        
        ts = context.tool_settings
        
        # Initialize colors for all paint modes
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint and ts.gpencil_paint.brush:
            self.__class__.old_gp_color = tuple(ts.gpencil_paint.brush.color)
            
        if hasattr(ts, 'image_paint') and ts.image_paint and ts.image_paint.brush:
            self.__class__.old_image_color = tuple(ts.image_paint.brush.color)
            
        if hasattr(ts, 'vertex_paint') and ts.vertex_paint and ts.vertex_paint.brush:
            self.__class__.old_vertex_color = tuple(ts.vertex_paint.brush.color)
        
        # Initialize palette color tracking
        paint_settings = None
        if context.mode == 'PAINT_GPENCIL':
            paint_settings = ts.gpencil_paint
        elif context.mode == 'PAINT_VERTEX':
            paint_settings = ts.vertex_paint
        else:
            paint_settings = ts.image_paint
            
        if paint_settings and paint_settings.palette and paint_settings.palette.colors.active:
            self.__class__.old_palette_color = tuple(paint_settings.palette.colors.active.color)
            
        # Start the timer
        COLOR_OT_monitor.is_running = True
        bpy.app.timers.register(self.__class__._timer_function)
        
        return {'FINISHED'}
        
    def execute(self, context):
        COLOR_OT_monitor.is_running = False
        return {'FINISHED'}