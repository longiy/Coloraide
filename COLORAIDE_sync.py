"""Color synchronization system"""

import bpy
from contextlib import contextmanager
from .COLORAIDE_utils import (
    rgb_to_lab, 
    lab_to_rgb,
    rgb_to_hsv,
    hsv_to_rgb,
    rgb_float_to_bytes,
    rgb_bytes_to_float,
    rgb_to_hex,
    hex_to_rgb
)

_UPDATING = False
_UPDATE_SOURCE = None

@contextmanager 
def update_lock(source=None):
    global _UPDATING, _UPDATE_SOURCE
    if _UPDATING:
        yield False
        return
    _UPDATING = True
    _UPDATE_SOURCE = source
    try:
        yield True
    finally:
        _UPDATING = False
        _UPDATE_SOURCE = None

def is_updating(source=None):
    if source:
        return _UPDATING and _UPDATE_SOURCE != source
    return _UPDATING

def sync_all(context, source, color):
    if is_updating(source):
        return
    
    # NEW: Block brush→coloraide updates during active color dynamics
    wm = context.window_manager
    if (source == 'brush' and 
        hasattr(wm, 'coloraide_dynamics') and 
        wm.coloraide_dynamics.strength > 0 and
        wm.coloraide_dynamics.running):
        return  # Skip brush→coloraide sync during dynamics
        
    with update_lock(source) as acquired:
        if not acquired:
            return
            
        # NEW: Update master color for dynamics when user changes Coloraide manually
        if (hasattr(wm, 'coloraide_dynamics') and 
            wm.coloraide_dynamics.strength > 0 and
            wm.coloraide_dynamics.running and
            source in ['wheel', 'picker', 'hsv', 'rgb', 'lab', 'hex', 'history', 'palette']):
            # User manually changed color - update master color for dynamics
            if hasattr(wm.coloraide_dynamics, 'master_color'):
                # Convert to RGB float for consistency
                if source == 'rgb':
                    rgb_float = rgb_bytes_to_float(color)
                elif source == 'lab':
                    rgb_float = lab_to_rgb(color)
                elif source == 'hsv':
                    hsv_norm = (color[0]/360.0, color[1]/100.0, color[2]/100.0)
                    rgb_float = hsv_to_rgb(hsv_norm)
                elif source == 'hex':
                    if isinstance(color, str):
                        rgb_float = hex_to_rgb(color)
                    else:
                        rgb_float = color
                else:
                    rgb_float = tuple(color[:3])
                
                wm.coloraide_dynamics.master_color = rgb_float
            
        # Rest of the function...
        
        # Convert input to RGB float (0-1)
        if source == 'rgb':
            rgb_float = rgb_bytes_to_float(color)
        elif source == 'lab':
            # Round near-zero values to zero
            current_lab = [
                0.0 if abs(wm.coloraide_lab.lightness) < 0.1 else float(wm.coloraide_lab.lightness),
                0.0 if abs(wm.coloraide_lab.a) < 0.1 else float(wm.coloraide_lab.a),
                0.0 if abs(wm.coloraide_lab.b) < 0.1 else float(wm.coloraide_lab.b)
            ]
            
            for i, val in enumerate(color):
                val = 0.0 if abs(float(val)) < 0.1 else float(val)
                if abs(val - current_lab[i]) > 0.0001:
                    current_lab[i] = val
                    
            rgb_float = lab_to_rgb(tuple(current_lab))
        elif source == 'hsv':
            # Convert from display values to normalized HSV
            hsv_norm = (color[0]/360.0, color[1]/100.0, color[2]/100.0)
            rgb_float = hsv_to_rgb(hsv_norm)
        elif source == 'hex':
            # CHANGE: Expect a hex string here, not rgb values
            if isinstance(color, str):
                rgb_float = hex_to_rgb(color)
            else:
                # Fall back if something else was passed
                rgb_float = color
        elif source == 'history':
            # Make sure this case is handled properly
            rgb_float = tuple(color[:3])
        else:
            rgb_float = tuple(color[:3])
        
        
        if context.mode == 'VERTEX_GREASE_PENCIL':
            ts = context.tool_settings
            # Add a special delay before updating the brush again
            # This helps break the feedback loop
            if hasattr(ts, 'gpencil_vertex_paint') and ts.gpencil_vertex_paint and ts.gpencil_vertex_paint.brush:
                import time
                time.sleep(0.01)  # Small delay to break update cycle
                ts.gpencil_vertex_paint.brush.color = rgb_float
                
        # Update RGB properties
        wm.coloraide_rgb.suppress_updates = True
        rgb_bytes = rgb_float_to_bytes(rgb_float)
        wm.coloraide_rgb.red = rgb_bytes[0]
        wm.coloraide_rgb.green = rgb_bytes[1]
        wm.coloraide_rgb.blue = rgb_bytes[2]
        wm.coloraide_rgb.suppress_updates = False
        
        # Update RGB preview colors too (like history colors)
        wm.coloraide_rgb.red_preview = (rgb_float[0], 0.0, 0.0)
        wm.coloraide_rgb.green_preview = (0.0, rgb_float[1], 0.0)
        wm.coloraide_rgb.blue_preview = (0.0, 0.0, rgb_float[2])
        
        # Update LAB
        wm.coloraide_lab.suppress_updates = True
        lab = rgb_to_lab(rgb_float)
        wm.coloraide_lab.lightness = round(lab[0])
        wm.coloraide_lab.a = round(lab[1])
        wm.coloraide_lab.b = round(lab[2])
        wm.coloraide_lab.suppress_updates = False
            
        # Update HSV
        wm.coloraide_hsv.suppress_updates = True
        hsv = rgb_to_hsv(rgb_float)
        wm.coloraide_hsv.hue = round(hsv[0] * 360.0)
        wm.coloraide_hsv.saturation = round(hsv[1] * 100.0)
        wm.coloraide_hsv.value = round(hsv[2] * 100.0)
        wm.coloraide_hsv.suppress_updates = False
            
        # Update picker mean 
        wm.coloraide_picker.suppress_updates = True
        wm.coloraide_picker.mean = rgb_float
        wm.coloraide_picker.suppress_updates = False
        
        # Update wheel
        wm.coloraide_wheel.suppress_updates = True
        wm.coloraide_wheel.color = (*rgb_float, 1.0)
        wm.coloraide_wheel.suppress_updates = False
        
        # Update hex
        wm.coloraide_hex.suppress_updates = True
        hex_value = rgb_to_hex(rgb_float)
        wm.coloraide_hex.value = hex_value
        wm.coloraide_hex.suppress_updates = False
        
        # Update all brush colors
        ts = context.tool_settings
        # Update Grease Pencil brush if available
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = rgb_float
            
        # Add support for Grease Pencil vertex paint
        if hasattr(ts, 'gpencil_vertex_paint') and ts.gpencil_vertex_paint and ts.gpencil_vertex_paint.brush:
            ts.gpencil_vertex_paint.brush.color = rgb_float
            
        # Update Image Paint brush if available
        if hasattr(ts, 'image_paint') and ts.image_paint and ts.image_paint.brush:
            ts.image_paint.brush.color = rgb_float
            
        # Update Vertex Paint brush if available
        if hasattr(ts, 'vertex_paint') and ts.vertex_paint and ts.vertex_paint.brush:
            ts.vertex_paint.brush.color = rgb_float