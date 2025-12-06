"""
Color monitor for Blender 5.0+
NEW APPROACH: Keep brush synced with Coloraide at all times,
so when Blender's native + button uses brush color, it's already correct!
"""

import bpy
from bpy.types import Operator
from .COLORAIDE_sync import sync_all, is_updating, is_updating_live_sync
from .COLORAIDE_brush_sync import is_brush_updating

class COLOR_OT_monitor(Operator):
    """Monitor brush and palette color changes."""
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    # State tracking
    is_running = False
    last_palette_name = None
    last_palette_color = None
    last_palette_count = 0
    last_brush_colors = {}
    last_coloraide_color = None  # NEW: Track Coloraide color
    _skip_palette_check_cycles = 0
    
    @classmethod
    def _get_brush_color(cls, paint_settings):
        """Safely get brush color from paint settings"""
        try:
            if paint_settings and paint_settings.brush:
                if hasattr(paint_settings, 'unified_paint_settings'):
                    ups = paint_settings.unified_paint_settings
                    if ups and hasattr(ups, 'use_unified_color') and ups.use_unified_color:
                        return tuple(ups.color[:3])
                return tuple(paint_settings.brush.color[:3])
        except:
            pass
        return None
    
    @classmethod
    def _set_brush_color(cls, paint_settings, color):
        """Set brush color"""
        try:
            if paint_settings and paint_settings.brush:
                if hasattr(paint_settings, 'unified_paint_settings'):
                    ups = paint_settings.unified_paint_settings
                    if ups and hasattr(ups, 'use_unified_color') and ups.use_unified_color:
                        ups.color = color
                        return True
                paint_settings.brush.color = color
                return True
        except:
            pass
        return False
    
    @classmethod
    def _get_active_paint_settings(cls, context):
        """Get the currently active paint settings (prioritizes current mode)"""
        ts = context.tool_settings
        current_mode = context.mode
        
        mode_to_settings = {
            'PAINT_GPENCIL': ts.gpencil_paint if hasattr(ts, 'gpencil_paint') else None,
            'VERTEX_GREASE_PENCIL': ts.gpencil_vertex_paint if hasattr(ts, 'gpencil_vertex_paint') else None,
            'PAINT_VERTEX': ts.vertex_paint if hasattr(ts, 'vertex_paint') else None,
            'PAINT_TEXTURE': ts.image_paint if hasattr(ts, 'image_paint') else None,
        }
        
        # PRIORITY 1: Current mode
        if current_mode in mode_to_settings:
            paint_settings = mode_to_settings[current_mode]
            if paint_settings and hasattr(paint_settings, 'palette') and paint_settings.palette:
                return paint_settings
        
        # PRIORITY 2: Fallback
        for paint_settings in mode_to_settings.values():
            if paint_settings and hasattr(paint_settings, 'palette') and paint_settings.palette:
                return paint_settings
        
        return None
    
    @classmethod
    def _timer_function(cls):
        """Timer callback - checks all paint modes for changes"""
        if not cls.is_running:
            return None
        
        if is_updating() or is_updating_live_sync() or is_brush_updating():
            return 0.1
        
        try:
            from .operators.PALETTE_OT import is_updating_palette
            if is_updating_palette():
                return 0.1
        except ImportError:
            pass
        
        try:
            context = bpy.context
            ts = context.tool_settings
            wm = context.window_manager
            
            # NEW: Keep brush synced with Coloraide at all times
            # This ensures when user clicks +, brush color = Coloraide color
            current_coloraide_color = tuple(wm.coloraide_picker.mean)
            
            if current_coloraide_color != cls.last_coloraide_color:
                cls.last_coloraide_color = current_coloraide_color
                
                # Sync brush to Coloraide immediately
                paint_settings = cls._get_active_paint_settings(context)
                if paint_settings:
                    cls._set_brush_color(paint_settings, current_coloraide_color)
            
            paint_modes = [
                ('gpencil_paint', ts.gpencil_paint if hasattr(ts, 'gpencil_paint') else None),
                ('gpencil_vertex_paint', ts.gpencil_vertex_paint if hasattr(ts, 'gpencil_vertex_paint') else None),
                ('vertex_paint', ts.vertex_paint if hasattr(ts, 'vertex_paint') else None),
                ('image_paint', ts.image_paint if hasattr(ts, 'image_paint') else None),
            ]
            
            # Get active paint settings
            paint_settings = cls._get_active_paint_settings(context)
            
            if paint_settings and paint_settings.palette:
                current_palette_name = paint_settings.palette.name
                current_count = len(paint_settings.palette.colors)
                
                # DETECT PALETTE SWITCH
                if current_palette_name != cls.last_palette_name:
                    print(f"\n*** PALETTE SWITCHED: '{cls.last_palette_name}' -> '{current_palette_name}' ({current_count} colors) ***")
                    
                    cls.last_palette_name = current_palette_name
                    cls.last_palette_count = current_count
                    
                    if paint_settings.palette.colors.active:
                        cls.last_palette_color = tuple(paint_settings.palette.colors.active.color[:3])
                    else:
                        cls.last_palette_color = None
                    
                    cls._skip_palette_check_cycles = 0
                    return 0.1
                
                # DETECT COLOR ADDITION
                if current_count > cls.last_palette_count:
                    print(f"\n*** COLOR ADDED TO '{current_palette_name}' ({cls.last_palette_count} -> {current_count}) ***")
                    
                    cls.last_palette_count = current_count
                    
                    coloraide_color = tuple(wm.coloraide_picker.mean)
                    print(f"    Coloraide: {coloraide_color}")
                    
                    if paint_settings.palette.colors.active:
                        palette_color = tuple(paint_settings.palette.colors.active.color[:3])
                        print(f"    Palette: {palette_color}")
                        
                        # If palette color doesn't match Coloraide, update it
                        if palette_color != coloraide_color:
                            print(f"    -> Updating palette to Coloraide color")
                            paint_settings.palette.colors.active.color = coloraide_color
                            cls.last_palette_color = coloraide_color
                        else:
                            print(f"    -> Already matches (brush was synced!)")
                            cls.last_palette_color = palette_color
                        
                        cls._skip_palette_check_cycles = 5
                        return 0.1
                
                # DETECT COLOR REMOVAL
                elif current_count < cls.last_palette_count:
                    print(f"\n*** COLOR REMOVED FROM '{current_palette_name}' ***")
                    cls.last_palette_count = current_count
                    
                    if paint_settings.palette.colors.active:
                        cls.last_palette_color = tuple(paint_settings.palette.colors.active.color[:3])
                    else:
                        cls.last_palette_color = None
                    
                    cls._skip_palette_check_cycles = 3
                    return 0.1
                
                # Skip cycles if needed
                if cls._skip_palette_check_cycles > 0:
                    cls._skip_palette_check_cycles -= 1
                    return 0.1
                
                # DETECT PALETTE COLOR CHANGE
                if paint_settings.palette.colors.active:
                    current_palette_color = tuple(paint_settings.palette.colors.active.color[:3])
                    
                    if current_palette_color != cls.last_palette_color:
                        cls.last_palette_color = current_palette_color
                        sync_all(context, 'palette', current_palette_color)
                        return 0.1
            
            # CHECK BRUSH COLOR CHANGES (from wheel/sliders changing)
            if not is_brush_updating():
                for mode_name, paint_settings in paint_modes:
                    if not paint_settings:
                        continue
                    
                    current_brush_color = cls._get_brush_color(paint_settings)
                    if not current_brush_color:
                        continue
                    
                    last_color = cls.last_brush_colors.get(mode_name)
                    
                    # Only sync if brush changed AND doesn't match Coloraide
                    # (to avoid fighting with our own syncing above)
                    if current_brush_color != last_color and current_brush_color != cls.last_coloraide_color:
                        cls.last_brush_colors[mode_name] = current_brush_color
                        
                        from .COLORAIDE_brush_sync import sync_coloraide_from_brush
                        sync_coloraide_from_brush(context, current_brush_color)
                        
                        return 0.1
        
        except Exception as e:
            print(f"Coloraide monitor error: {e}")
            import traceback
            traceback.print_exc()
        
        return 0.1
    
    def invoke(self, context, event):
        """Start the color monitor"""
        print("\n=== COLORAIDE MONITOR STARTING ===")
        print("NEW: Keeping brush synced with Coloraide at all times")
        print("This makes native + button use Coloraide color!")
        print("="*40 + "\n")
        
        # Reset state
        COLOR_OT_monitor.is_running = False
        COLOR_OT_monitor.last_palette_name = None
        COLOR_OT_monitor.last_palette_color = None
        COLOR_OT_monitor.last_palette_count = 0
        COLOR_OT_monitor.last_brush_colors = {}
        COLOR_OT_monitor.last_coloraide_color = None
        COLOR_OT_monitor._skip_palette_check_cycles = 0
        
        ts = context.tool_settings
        wm = context.window_manager
        
        # Initialize Coloraide tracking
        COLOR_OT_monitor.last_coloraide_color = tuple(wm.coloraide_picker.mean)
        
        paint_modes = [
            ('gpencil_paint', ts.gpencil_paint if hasattr(ts, 'gpencil_paint') else None),
            ('gpencil_vertex_paint', ts.gpencil_vertex_paint if hasattr(ts, 'gpencil_vertex_paint') else None),
            ('vertex_paint', ts.vertex_paint if hasattr(ts, 'vertex_paint') else None),
            ('image_paint', ts.image_paint if hasattr(ts, 'image_paint') else None),
        ]
        
        # Initialize using current mode's paint settings
        paint_settings = self._get_active_paint_settings(context)
        if paint_settings and paint_settings.palette:
            COLOR_OT_monitor.last_palette_name = paint_settings.palette.name
            COLOR_OT_monitor.last_palette_count = len(paint_settings.palette.colors)
            
            if paint_settings.palette.colors.active:
                COLOR_OT_monitor.last_palette_color = tuple(paint_settings.palette.colors.active.color[:3])
        
        # Initialize brush colors
        for mode_name, paint_settings in paint_modes:
            if paint_settings:
                brush_color = self._get_brush_color(paint_settings)
                if brush_color:
                    COLOR_OT_monitor.last_brush_colors[mode_name] = brush_color
        
        # Start timer
        COLOR_OT_monitor.is_running = True
        bpy.app.timers.register(self.__class__._timer_function)
        
        return {'FINISHED'}
    
    def execute(self, context):
        """Stop the color monitor"""
        COLOR_OT_monitor.is_running = False
        return {'FINISHED'}