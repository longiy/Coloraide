# COLORAIDE_monitor.py
import bpy
import time
from bpy.types import Operator
from .COLORAIDE_brush_sync import sync_picker_from_brush, is_brush_updating, check_brush_color
from .COLORAIDE_utils import get_blender_version_category, get_gpencil_brush

class COLOR_OT_monitor(Operator):
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    old_gp_color = None
    old_image_color = None
    old_vertex_color = None
    old_gp_vertex_color = None
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
            current_mode = context.mode
            
            # Get brush and old color reference based on mode
            brush = None
            old_color = None
            
            if current_mode in ('PAINT_GPENCIL', 'PAINT_GREASE_PENCIL'):
                brush = get_gpencil_brush(context, for_vertex=False)
                old_color = cls.old_gp_color
            elif current_mode in ('VERTEX_GPENCIL', 'VERTEX_GREASE_PENCIL'):
                brush = get_gpencil_brush(context, for_vertex=True)
                old_color = cls.old_gp_vertex_color
            elif current_mode == 'PAINT_VERTEX':
                brush = ts.vertex_paint.brush if hasattr(ts, 'vertex_paint') else None
                old_color = cls.old_vertex_color
            elif current_mode == 'PAINT_TEXTURE':
                brush = ts.image_paint.brush if hasattr(ts, 'image_paint') else None
                old_color = cls.old_image_color
                
            # Check if color changed
            if brush:
                curr_color = tuple(brush.color)
                if curr_color != old_color:
                    # Update stored color
                    if current_mode in ('PAINT_GPENCIL', 'PAINT_GREASE_PENCIL'):
                        cls.old_gp_color = curr_color
                    elif current_mode in ('VERTEX_GPENCIL', 'VERTEX_GREASE_PENCIL'):
                        cls.old_gp_vertex_color = curr_color
                    elif current_mode == 'PAINT_VERTEX':
                        cls.old_vertex_color = curr_color
                    else:
                        cls.old_image_color = curr_color
                    
                    # Update Coloraide if not already updating
                    if not is_brush_updating():
                        sync_picker_from_brush(context, curr_color)
                    
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
                    
        # Initialize colors for GP vertex paint
        if hasattr(ts, 'gpencil_vertex_paint') and ts.gpencil_vertex_paint and ts.gpencil_vertex_paint.brush:
            self.__class__.old_gp_vertex_color = tuple(ts.gpencil_vertex_paint.brush.color)   
            
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