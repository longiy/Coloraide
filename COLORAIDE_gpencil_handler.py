"""Handler system for Grease Pencil vertex paint color changes"""

import bpy
from bpy.app.handlers import persistent
from .COLORAIDE_brush_sync import sync_picker_from_brush, is_brush_updating

def update_from_gpencil_brush(self, context):
    """Handler for Grease Pencil vertex paint brush color changes"""
    if is_brush_updating():
        return
        
    if not hasattr(context, "tool_settings"):
        return
        
    ts = context.tool_settings
    if hasattr(ts, 'gpencil_vertex_paint') and ts.gpencil_vertex_paint and ts.gpencil_vertex_paint.brush:
        color = tuple(ts.gpencil_vertex_paint.brush.color)
        sync_picker_from_brush(context, color)

@persistent
def register_gpencil_handlers(dummy):
    """Register update handlers for Grease Pencil brushes"""
    # Remove any existing handlers first
    for cls in bpy.types.Brush.__subclasses__():
        if hasattr(cls, "color"):
            # Check if our handler is already registered
            if update_from_gpencil_brush in cls.color._updating_callbacks:
                cls.color._updating_callbacks.remove(update_from_gpencil_brush)
            # Add our handler
            cls.color._updating_callbacks.append(update_from_gpencil_brush)

def unregister_gpencil_handlers():
    """Unregister update handlers"""
    for cls in bpy.types.Brush.__subclasses__():
        if hasattr(cls, "color"):
            if update_from_gpencil_brush in cls.color._updating_callbacks:
                cls.color._updating_callbacks.remove(update_from_gpencil_brush)