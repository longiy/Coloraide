"""
Color monitor for Blender 5.0+
Simple, robust version that works with palettes.
Based on proven working approach - no complex mode management.
"""

import bpy
from bpy.types import Operator
from .COLORAIDE_sync import sync_all
from .COLORAIDE_brush_sync import is_brush_updating

class COLOR_OT_monitor(Operator):
    """
    Monitor brush and palette color changes.
    Simple timer-based approach that just works.
    """
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    # State tracking
    is_running = False
    last_palette_color = None
    last_brush_colors = {}  # Dict to track each paint mode separately
    
    @classmethod
    def _get_brush_color(cls, paint_settings):
        """Safely get brush color from paint settings"""
        try:
            if paint_settings and paint_settings.brush:
                # Check if unified color is enabled
                if hasattr(paint_settings, 'unified_paint_settings'):
                    ups = paint_settings.unified_paint_settings
                    if ups and hasattr(ups, 'use_unified_color') and ups.use_unified_color:
                        return tuple(ups.color[:3])
                
                # Fall back to brush color
                return tuple(paint_settings.brush.color[:3])
        except:
            pass
        return None
    
    @classmethod
    def _timer_function(cls):
        """Timer callback - checks all paint modes for changes"""
        if not cls.is_running:
            return None
        
        try:
            context = bpy.context
            ts = context.tool_settings
            
            # List of all paint settings to check
            paint_modes = [
                ('gpencil_paint', ts.gpencil_paint if hasattr(ts, 'gpencil_paint') else None),
                ('gpencil_vertex_paint', ts.gpencil_vertex_paint if hasattr(ts, 'gpencil_vertex_paint') else None),
                ('vertex_paint', ts.vertex_paint if hasattr(ts, 'vertex_paint') else None),
                ('image_paint', ts.image_paint if hasattr(ts, 'image_paint') else None),
            ]
            
            # CHECK 1: Palette color changes (highest priority)
            # Check ALL paint modes for an active palette
            for mode_name, paint_settings in paint_modes:
                if not paint_settings:
                    continue
                
                try:
                    if paint_settings.palette and paint_settings.palette.colors.active:
                        current_palette_color = tuple(paint_settings.palette.colors.active.color[:3])
                        
                        # Compare with last known palette color
                        if current_palette_color != cls.last_palette_color:
                            cls.last_palette_color = current_palette_color
                            
                            # Update Coloraide from palette
                            sync_all(context, 'palette', current_palette_color)
                            
                            # Also update the brush to match palette (standard Blender behavior)
                            if paint_settings.brush:
                                # Check if unified color is in use
                                if hasattr(paint_settings, 'unified_paint_settings'):
                                    ups = paint_settings.unified_paint_settings
                                    if ups and hasattr(ups, 'use_unified_color') and ups.use_unified_color:
                                        ups.color = current_palette_color
                                    else:
                                        paint_settings.brush.color = current_palette_color
                                else:
                                    paint_settings.brush.color = current_palette_color
                            
                            # Update tracking for this mode's brush
                            cls.last_brush_colors[mode_name] = current_palette_color
                            
                            # Early return - palette changes take priority
                            return 0.1
                except:
                    pass
            
            # CHECK 2: Brush color changes (wheel, sliders, etc.)
            # Only check if not currently updating from brush
            if not is_brush_updating():
                for mode_name, paint_settings in paint_modes:
                    if not paint_settings:
                        continue
                    
                    current_brush_color = cls._get_brush_color(paint_settings)
                    if not current_brush_color:
                        continue
                    
                    # Get last known color for this mode
                    last_color = cls.last_brush_colors.get(mode_name)
                    
                    # Check if changed
                    if current_brush_color != last_color:
                        cls.last_brush_colors[mode_name] = current_brush_color
                        
                        # Update Coloraide from brush
                        from .COLORAIDE_brush_sync import sync_coloraide_from_brush
                        sync_coloraide_from_brush(context, current_brush_color)
                        
                        # Don't check other modes this cycle
                        return 0.1
        
        except Exception as e:
            print(f"Coloraide monitor error: {e}")
        
        return 0.1  # Check every 0.1 seconds
    
    def invoke(self, context, event):
        """Start the color monitor"""
        # Reset state
        COLOR_OT_monitor.is_running = False
        COLOR_OT_monitor.last_palette_color = None
        COLOR_OT_monitor.last_brush_colors = {}
        
        ts = context.tool_settings
        
        # Initialize palette tracking
        paint_modes = [
            ('gpencil_paint', ts.gpencil_paint if hasattr(ts, 'gpencil_paint') else None),
            ('gpencil_vertex_paint', ts.gpencil_vertex_paint if hasattr(ts, 'gpencil_vertex_paint') else None),
            ('vertex_paint', ts.vertex_paint if hasattr(ts, 'vertex_paint') else None),
            ('image_paint', ts.image_paint if hasattr(ts, 'image_paint') else None),
        ]
        
        # Find current palette color
        for mode_name, paint_settings in paint_modes:
            if paint_settings and paint_settings.palette and paint_settings.palette.colors.active:
                COLOR_OT_monitor.last_palette_color = tuple(paint_settings.palette.colors.active.color[:3])
                break
        
        # Initialize brush colors for all modes
        for mode_name, paint_settings in paint_modes:
            if paint_settings:
                brush_color = self._get_brush_color(paint_settings)
                if brush_color:
                    COLOR_OT_monitor.last_brush_colors[mode_name] = brush_color
        
        # Start the timer
        COLOR_OT_monitor.is_running = True
        bpy.app.timers.register(self.__class__._timer_function)
        
        return {'FINISHED'}
    
    def execute(self, context):
        """Stop the color monitor"""
        COLOR_OT_monitor.is_running = False
        return {'FINISHED'}