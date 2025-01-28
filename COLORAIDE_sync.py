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
        
    with update_lock(source) as acquired:
        if not acquired:
            return
            
        wm = context.window_manager
        
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
            rgb_float = hex_to_rgb(color)
        else:
            rgb_float = tuple(color[:3])
            
        # Update RGB properties
        wm.coloraide_rgb.suppress_updates = True
        rgb_bytes = rgb_float_to_bytes(rgb_float)
        wm.coloraide_rgb.red = rgb_bytes[0]
        wm.coloraide_rgb.green = rgb_bytes[1]
        wm.coloraide_rgb.blue = rgb_bytes[2]
        wm.coloraide_rgb.suppress_updates = False
        
        # Update LAB
        if source != 'lab':
            wm.coloraide_lab.suppress_updates = True
            lab = rgb_to_lab(rgb_float)
            wm.coloraide_lab.lightness = round(lab[0])
            wm.coloraide_lab.a = round(lab[1])
            wm.coloraide_lab.b = round(lab[2])
            wm.coloraide_lab.suppress_updates = False
            
        # Update HSV
        if source != 'hsv':
            wm.coloraide_hsv.suppress_updates = True
            hsv = rgb_to_hsv(rgb_float)
            wm.coloraide_hsv.hue = round(hsv[0] * 360.0)
            wm.coloraide_hsv.saturation = round(hsv[1] * 100.0)
            wm.coloraide_hsv.value = round(hsv[2] * 100.0)
            wm.coloraide_hsv.suppress_updates = False
            
        # Update picker mean only (removed current)
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
        
        # Update brush colors
        ts = context.tool_settings
        if hasattr(ts, 'gpencil_paint') and ts.gpencil_paint.brush:
            ts.gpencil_paint.brush.color = rgb_float
            
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = rgb_float
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = rgb_float