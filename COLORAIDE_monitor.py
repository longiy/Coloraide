# COLORAIDE_monitor.py
import bpy
from .COLORAIDE_brush_sync import sync_picker_from_brush, is_brush_updating

def check_brush_color(context, paint_settings):
    """Get current brush color from paint settings"""
    if not paint_settings or not paint_settings.brush:
        return None
        
    ts = context.tool_settings
    if ts.unified_paint_settings.use_unified_color:
        return tuple(ts.unified_paint_settings.color)
    
    if paint_settings.palette and paint_settings.palette.colors.active:
        return tuple(paint_settings.palette.colors.active.color)
        
    return tuple(paint_settings.brush.color)

class ColorMonitorState:
    """Class to store color monitor state"""
    old_gp_color = None
    old_image_color = None
    old_vertex_color = None
    old_palette_color = None
    timer_handler = None
    is_running = False

def check_color_change(context, paint_settings, old_color):
    """Check for color changes in paint settings"""
    if not paint_settings:
        return None, old_color
        
    curr_color = check_brush_color(context, paint_settings)
    if not curr_color:
        return None, old_color
        
    if curr_color != old_color:
        return curr_color, curr_color
            
    return None, old_color

def monitor_colors():
    """Timer function to monitor color changes"""
    try:
        context = bpy.context
        ts = context.tool_settings
        color_changed = False
        update_color = None
        
        # Get current paint settings based on mode
        paint_settings = None
        old_color = None
        
        if context.mode == 'PAINT_GPENCIL':
            paint_settings = ts.gpencil_paint
            old_color = ColorMonitorState.old_gp_color
        elif context.mode == 'PAINT_VERTEX':
            paint_settings = ts.vertex_paint
            old_color = ColorMonitorState.old_vertex_color
        else:
            paint_settings = ts.image_paint
            old_color = ColorMonitorState.old_image_color

        # Check for color changes including palette
        if paint_settings:
            # Check active palette color
            if paint_settings.palette and paint_settings.palette.colors.active:
                curr_palette_color = tuple(paint_settings.palette.colors.active.color)
                if curr_palette_color != ColorMonitorState.old_palette_color:
                    color_changed = True
                    update_color = curr_palette_color
                    ColorMonitorState.old_palette_color = curr_palette_color
            
            # Check brush color
            if not color_changed:  # Only check if palette didn't change
                new_color, old_color = check_color_change(
                    context, 
                    paint_settings,
                    old_color
                )
                if new_color:
                    color_changed = True
                    update_color = new_color
        
        # Store updated old color based on mode
        if context.mode == 'PAINT_GPENCIL':
            ColorMonitorState.old_gp_color = old_color
        elif context.mode == 'PAINT_VERTEX':
            ColorMonitorState.old_vertex_color = old_color
        else:
            ColorMonitorState.old_image_color = old_color
        
        # Update Coloraide if any color changed
        if color_changed and update_color and not is_brush_updating():
            sync_picker_from_brush(context, update_color)
            
    except Exception as e:
        print(f"Color monitor error: {e}")
        
    # Return true to keep the timer running
    if ColorMonitorState.is_running:
        return 0.1  # Run every 0.1 seconds
    return None

def start_color_monitor():
    """Start the color monitor timer"""
    if not ColorMonitorState.is_running:
        ColorMonitorState.is_running = True
        # Initialize tracking colors
        context = bpy.context
        ts = context.tool_settings
        
        # Initialize colors for all paint modes
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint and ts.gpencil_paint.brush:
            ColorMonitorState.old_gp_color = tuple(ts.gpencil_paint.brush.color)
            
        if hasattr(ts, 'image_paint') and ts.image_paint and ts.image_paint.brush:
            ColorMonitorState.old_image_color = tuple(ts.image_paint.brush.color)
            
        if hasattr(ts, 'vertex_paint') and ts.vertex_paint and ts.vertex_paint.brush:
            ColorMonitorState.old_vertex_color = tuple(ts.vertex_paint.brush.color)
        
        # Initialize palette color tracking
        paint_settings = None
        if context.mode == 'PAINT_GPENCIL':
            paint_settings = ts.gpencil_paint
        elif context.mode == 'PAINT_VERTEX':
            paint_settings = ts.vertex_paint
        else:
            paint_settings = ts.image_paint
            
        if paint_settings and paint_settings.palette and paint_settings.palette.colors.active:
            ColorMonitorState.old_palette_color = tuple(paint_settings.palette.colors.active.color)
            
        # Start the timer
        if not ColorMonitorState.timer_handler:
            ColorMonitorState.timer_handler = bpy.app.timers.register(monitor_colors)

def stop_color_monitor():
    """Stop the color monitor timer"""
    ColorMonitorState.is_running = False
    if ColorMonitorState.timer_handler and ColorMonitorState.timer_handler in bpy.app.timers.registered:
        bpy.app.timers.unregister(ColorMonitorState.timer_handler)
    ColorMonitorState.timer_handler = None

# Operator just for starting/stopping the monitor
class COLOR_OT_monitor(bpy.types.Operator):
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        start_color_monitor()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(COLOR_OT_monitor)
    
def unregister():
    stop_color_monitor()
    bpy.utils.unregister_class(COLOR_OT_monitor)