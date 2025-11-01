"""
Color monitor for Blender 5.0+
Simplified to only monitor current mode's brush color.
"""

import bpy
from bpy.types import Operator
from .COLORAIDE_mode_manager import ModeManager
from .COLORAIDE_brush_sync import sync_coloraide_from_brush, is_brush_updating

class COLOR_OT_monitor(Operator):
    """
    Modal operator that monitors brush color changes and syncs to Coloraide.
    Runs continuously in background after startup.
    """
    bl_idname = "color.monitor"
    bl_label = "Monitor Color Changes"
    bl_options = {'INTERNAL'}
    
    # Class variables for state tracking
    _last_mode = None
    _last_color = None
    is_running = False
    
    @classmethod
    def _timer_function(cls):
        """
        Timer callback function - monitors current mode's brush color.
        Checks every 0.1 seconds for color changes.
        """
        if not cls.is_running:
            return None
        
        try:
            context = bpy.context
            
            # Get current mode
            current_mode = ModeManager.get_current_mode(context)
            
            # Handle mode switches
            if current_mode != cls._last_mode:
                cls._last_mode = current_mode
                cls._last_color = None  # Reset color tracking on mode change
                
                # Sync Coloraide to new mode's brush color
                if current_mode:
                    brush_color = ModeManager.get_brush_color(context)
                    if brush_color:
                        sync_coloraide_from_brush(context, brush_color)
            
            # Monitor current mode's brush color
            if current_mode and not is_brush_updating():
                current_color = ModeManager.get_brush_color(context)
                
                if current_color and current_color != cls._last_color:
                    cls._last_color = current_color
                    sync_coloraide_from_brush(context, current_color)
        
        except Exception as e:
            print(f"Color monitor error: {e}")
        
        return 0.1  # Check every 0.1 seconds
    
    def invoke(self, context, event):
        """Initialize and start the color monitor."""
        # Reset state
        COLOR_OT_monitor.is_running = False
        COLOR_OT_monitor._last_mode = None
        COLOR_OT_monitor._last_color = None
        
        # Initialize with current mode and color
        current_mode = ModeManager.get_current_mode(context)
        if current_mode:
            COLOR_OT_monitor._last_mode = current_mode
            brush_color = ModeManager.get_brush_color(context)
            if brush_color:
                COLOR_OT_monitor._last_color = brush_color
        
        # Start the timer
        COLOR_OT_monitor.is_running = True
        bpy.app.timers.register(self.__class__._timer_function)
        
        return {'FINISHED'}
    
    def execute(self, context):
        """Stop the color monitor."""
        COLOR_OT_monitor.is_running = False
        return {'FINISHED'}
