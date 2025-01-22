"""
Utility functions for Coloraide addon.
Contains shared color conversion and helper functions.
"""

import numpy as np
from math import pow

"""Centralized color update flag management"""

# Global update flags for all possible components
UPDATE_FLAGS = {
    'picker': False,
    'rgb': False,
    'hsv': False,
    'lab': False, 
    'hex': False,
    'wheel': False
}

def is_any_update_in_progress():
    """Check if any color component is currently updating"""
    return any(UPDATE_FLAGS.values())

def is_updating(component_name):
    """Check if specific component is updating"""
    return UPDATE_FLAGS.get(component_name, False)

class UpdateFlags:
    """Context manager for handling update flags"""
    def __init__(self, component_name):
        self.component_name = component_name
        
    def __enter__(self):
        UPDATE_FLAGS[self.component_name] = True
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        UPDATE_FLAGS[self.component_name] = False

def rgb_to_hsv(rgb):
    """Convert RGB values in range 0-1 to HSV values in range 0-1"""
    r, g, b = rgb
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val

    # Calculate hue
    if diff == 0:
        h = 0
    elif max_val == r:
        h = (60 * ((g - b) / diff) + 360) % 360 / 360
    elif max_val == g:
        h = (60 * ((b - r) / diff) + 120) / 360
    else:
        h = (60 * ((r - g) / diff) + 240) / 360

    # Calculate saturation
    s = 0 if max_val == 0 else diff / max_val

    # Value is simply the max
    v = max_val

    return (h, s, v)

def hsv_to_rgb(hsv):
    """Convert HSV values in range 0-1 to RGB values in range 0-1"""
    h, s, v = hsv
    
    if s == 0:
        return (v, v, v)
    
    h *= 6
    i = int(h)
    f = h - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    
    if i == 0:
        return (v, t, p)
    elif i == 1:
        return (q, v, p)
    elif i == 2:
        return (p, v, t)
    elif i == 3:
        return (p, q, v)
    elif i == 4:
        return (t, p, v)
    else:
        return (v, p, q)

def rgb_to_xyz(rgb):
    """Convert RGB values to XYZ color space (D50)"""
    r, g, b = rgb
    
    # Convert to linear RGB
    def to_linear(c):
        c = max(0, min(1, c))
        if c <= 0.04045:
            return c / 12.92
        return pow((c + 0.055) / 1.055, 2.4)
    
    r = to_linear(r)
    g = to_linear(g)
    b = to_linear(b)
    
    # Convert to XYZ
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    
    # Bradford transformation D65 -> D50
    x_d50 = x * 1.0478112 + y * 0.0228866 + z * -0.0501270
    y_d50 = x * 0.0295424 + y * 0.9904844 + z * -0.0170491
    z_d50 = x * -0.0092345 + y * 0.0150436 + z * 0.7521316
    
    return (x_d50, y_d50, z_d50)

def xyz_to_lab(xyz):
    """Convert XYZ values to LAB color space"""
    x, y, z = xyz
    
    # D50 reference white
    ref_x = 0.96422
    ref_y = 1.00000
    ref_z = 0.82521
    
    # Constants
    epsilon = 216/24389
    kappa = 24389/27
    
    # Scale by white point
    xr = x / ref_x
    yr = y / ref_y
    zr = z / ref_z
    
    # Conversion function
    def f(t):
        if t > epsilon:
            return pow(t, 1/3)
        return (kappa * t + 16) / 116
    
    fx = f(xr)
    fy = f(yr)
    fz = f(zr)
    
    L = max(0, min(100, 116 * fy - 16))
    a = max(-128, min(127, 500 * (fx - fy)))
    b = max(-128, min(127, 200 * (fy - fz)))
    
    return (L, a, b)

def lab_to_xyz(lab):
    """Convert LAB values to XYZ color space"""
    L, a, b = lab
    
    # Constants
    epsilon = 216/24389
    kappa = 24389/27
    
    # D50 reference white
    ref_x = 0.96422
    ref_y = 1.00000
    ref_z = 0.82521
    
    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200
    
    def f_inv(t):
        if t**3 > epsilon:
            return t**3
        return (116 * t - 16) / kappa
    
    x = ref_x * f_inv(fx)
    y = ref_y * f_inv(fy)
    z = ref_z * f_inv(fz)
    
    return (x, y, z)

def xyz_to_rgb(xyz):
    """Convert XYZ values to RGB color space"""
    x, y, z = xyz
    
    # Bradford transformation D50 -> D65
    x_d65 = x * 0.9555766 + y * -0.0230393 + z * 0.0631636
    y_d65 = x * -0.0282895 + y * 1.0099416 + z * 0.0210077
    z_d65 = x * 0.0122982 + y * -0.0204830 + z * 1.3299098
    
    # Convert to RGB
    r = x_d65 *  3.2404542 - y_d65 * 1.5371385 - z_d65 * 0.4985314
    g = x_d65 * -0.9692660 + y_d65 * 1.8760108 + z_d65 * 0.0415560
    b = x_d65 *  0.0556434 - y_d65 * 0.2040259 + z_d65 * 1.0572252
    
    # Convert to sRGB
    def to_srgb(c):
        if c <= 0.0031308:
            return 12.92 * c
        return 1.055 * pow(abs(c), 1/2.4) - 0.055
    
    r = max(0, min(1, to_srgb(r)))
    g = max(0, min(1, to_srgb(g)))
    b = max(0, min(1, to_srgb(b)))
    
    return (r, g, b)

# Color space conversion convenience functions
def rgb_to_lab(rgb):
    """Convert RGB to LAB"""
    xyz = rgb_to_xyz(rgb)
    return xyz_to_lab(xyz)

def lab_to_rgb(lab):
    """Convert LAB to RGB"""
    xyz = lab_to_xyz(lab)
    return xyz_to_rgb(xyz)

# Utility functions for color manipulation
def rgb_bytes_to_float(rgb_bytes):
    """Convert RGB bytes (0-255) to float values (0-1)"""
    return tuple(c / 255 for c in rgb_bytes)

def rgb_float_to_bytes(rgb_float):
    """Convert RGB float values (0-1) to bytes (0-255)"""
    return tuple(round(c * 255) for c in rgb_float)

def hex_to_rgb(hex_str):
    """Convert hex string to RGB float values"""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) != 6:
        return (0.0, 0.0, 0.0)
    try:
        rgb_bytes = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return rgb_bytes_to_float(rgb_bytes)
    except ValueError:
        return (0.0, 0.0, 0.0)

def rgb_to_hex(rgb_float):
    """Convert RGB float values to hex string"""
    rgb_bytes = rgb_float_to_bytes(rgb_float)
    return "#{:02X}{:02X}{:02X}".format(*rgb_bytes)

# Color statistics functions
def color_statistics(colors):
    """Calculate color statistics for an array of colors"""
    if not colors.size:
        return None
        
    colors = np.array(colors)
    stats = {
        'mean': np.mean(colors, axis=0),
        'median': np.median(colors, axis=0),
        'min': np.min(colors, axis=0),
        'max': np.max(colors, axis=0)
    }
    return stats