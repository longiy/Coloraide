"""
Mode-aware brush access system for Blender 5.0+
Provides unified interface for accessing mode-specific unified paint settings and brushes.
"""

import bpy

class ModeManager:
    """
    Manages access to mode-specific paint settings and brushes in Blender 5.0+
    
    In Blender 5.0, unified_paint_settings moved from tool_settings to mode-specific
    Paint structs (sculpt, image_paint, vertex_paint, weight_paint).
    This class provides a clean interface to access the correct settings based on context.
    """
    
    MODE_MAP = {
        'SCULPT': 'sculpt',
        'PAINT_TEXTURE': 'image_paint',
        'PAINT_VERTEX': 'vertex_paint',
        'PAINT_WEIGHT': 'weight_paint',
        'PAINT_GPENCIL': 'gpencil_paint',
        'VERTEX_GREASE_PENCIL': 'gpencil_vertex_paint',
    }
    
    @staticmethod
    def get_current_mode(context):
        """
        Get the current paint mode identifier.
        
        Args:
            context: Blender context
        
        Returns:
            str: Mode identifier or None if not in a paint mode
        """
        return context.mode if context.mode in ModeManager.MODE_MAP else None
    
    @staticmethod
    def get_paint_settings(context):
        """Get paint settings with improved Image Editor detection"""
        ts = context.tool_settings
        
        # Priority 1: If in Image Editor, always use image_paint
        if hasattr(context, 'space_data') and context.space_data:
            if context.space_data.type == 'IMAGE_EDITOR':
                return ts.image_paint
        
        # Priority 2: Use context.mode
        mode = context.mode
        if mode in ModeManager.MODE_MAP:
            paint_attr = ModeManager.MODE_MAP[mode]
            return getattr(ts, paint_attr, None)
        
        # Priority 3: Check if we have any active paint brush
        if ts.image_paint and ts.image_paint.brush:
            return ts.image_paint
        
        return None
    
    @staticmethod
    def get_unified_paint_settings(context):
        """
        Get unified_paint_settings for current mode (Blender 5.0+ API).
        
        Args:
            context: Blender context
        
        Returns:
            UnifiedPaintSettings or None
        """
        paint_settings = ModeManager.get_paint_settings(context)
        if not paint_settings:
            return None
        
        return getattr(paint_settings, 'unified_paint_settings', None)
    
    @staticmethod
    def get_current_brush(context):
        """
        Get the active brush for current mode.
        
        Args:
            context: Blender context
        
        Returns:
            Brush object or None
        """
        paint_settings = ModeManager.get_paint_settings(context)
        if not paint_settings:
            return None
        
        return getattr(paint_settings, 'brush', None)

        # NEW: If no brush, try to activate default
        if not brush and paint_settings:
            # Get or create default brush for this paint mode
            bpy.ops.paint.brush_select(image_tool='DRAW')  # or similar
    
    @staticmethod
    def get_brush_color(context):
        """
        Get current brush color (scene linear color space).
        Respects unified color settings.
        
        Args:
            context: Blender context
        
        Returns:
            tuple: (r, g, b) in scene linear space, or None
        """
        paint_settings = ModeManager.get_paint_settings(context)
        if not paint_settings:
            return None
        
        # Check if unified color is enabled
        ups = ModeManager.get_unified_paint_settings(context)
        if ups and getattr(ups, 'use_unified_color', False):
            return tuple(ups.color[:3])
        
        # Fall back to brush color
        brush = paint_settings.brush
        if brush:
            return tuple(brush.color[:3])
        
        return None
    
    @staticmethod
    def set_brush_color(context, color):
        """
        Set brush color for current mode (scene linear color space).
        Updates unified color if enabled, otherwise updates brush color.
        
        Args:
            context: Blender context
            color: tuple of (r, g, b) in scene linear space [0.0, 1.0]
        
        Returns:
            bool: True if successful, False otherwise
        """
        paint_settings = ModeManager.get_paint_settings(context)
        if not paint_settings:
            return False
        
        color = tuple(color[:3])
        
        # Check if unified color is enabled
        ups = ModeManager.get_unified_paint_settings(context)
        if ups and getattr(ups, 'use_unified_color', False):
            ups.color = color
            return True
        
        # Update brush color
        brush = paint_settings.brush
        if brush:
            brush.color = color
            return True
        
        return False
    
    @staticmethod
    def is_paint_mode(context):
        """
        Check if current mode is a paint mode.
        
        Args:
            context: Blender context
        
        Returns:
            bool: True if in a paint mode
        """
        return ModeManager.get_current_mode(context) is not None


__all__ = ['ModeManager']
