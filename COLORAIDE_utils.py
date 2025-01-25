"""
Utility functions for Coloraide addon.
Contains shared color conversion and helper functions.
"""

import numpy as np
from math import pow

"""Centralized color update flag management"""

# Global update state
_UPDATING_FROM = None

def is_updating(component_name):
    """Check if an update is in progress and prevent cycles"""
    return _UPDATING_FROM is not None and _UPDATING_FROM != component_name

class UpdateFlags:
    """Context manager for handling update flags"""
    def __init__(self, source):
        self.source = source
        self.previous = None
        
    def __enter__(self):
        global _UPDATING_FROM
        self.previous = _UPDATING_FROM
        _UPDATING_FROM = self.source
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _UPDATING_FROM
        _UPDATING_FROM = self.previous

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
    
    # Wrap 1.0 back to 0.0
    if h == 1.0:
        h = 0.0
    
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

def lab_to_xyz(lab):
    """Convert from LAB to XYZ D50 with Photoshop-matching behavior"""
    L, a, b = lab
    
    # ICC constants (same as Photoshop)
    epsilon = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    
    # D50 reference white (Photoshop values)
    ref_x = 0.96422
    ref_y = 1.00000
    ref_z = 0.82521
    
    # Special handling for L=0 to match Photoshop
    if L < 0.01:  # Treat very small L values as 0
        fy = 16.0 / 116.0
    else:
        fy = (L + 16.0) / 116.0
    
    # Adjust fx and fz calculation for extreme a/b values
    fx = fy + (a / 500.0)
    fz = fy - (b / 200.0)
    
    # Modified f_inv function to better handle extreme values
    def f_inv(t):
        t3 = t * t * t
        if t > 6.0/29.0:
            return t3
        return (116.0 * t - 16.0) / kappa
    
    x = ref_x * f_inv(fx)
    y = ref_y * f_inv(fy)
    z = ref_z * f_inv(fz)
    
    # Less aggressive clamping
    x = max(0, x)
    y = max(0, y)
    z = max(0, z)
    
    return (x, y, z)

def xyz_to_lab(xyz):
    """Convert from XYZ D50 to LAB"""
    x, y, z = xyz
    
    # D50 reference white
    ref_x = 0.96422
    ref_y = 1.00000
    ref_z = 0.82521
    
    # Constants
    epsilon = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    
    # Scale by white point
    xr = x / ref_x
    yr = y / ref_y
    zr = z / ref_z
    
    # ICC standard conversion function
    def f(t):
        if t > epsilon:
            return pow(t, 1.0/3.0)
        return (kappa * t + 16) / 116
    
    fx = f(xr)
    fy = f(yr)
    fz = f(zr)
    
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    
    # Clamp values to valid ranges
    L = max(0, min(100, L))
    a = max(-128, min(127, a))
    b = max(-128, min(127, b))
    
    return (L, a, b)

def xyz_to_rgb(xyz):
    """Convert from XYZ D50 to sRGB with Photoshop-matching behavior"""
    x, y, z = xyz
    
    # Modified Bradford matrix (closer to Photoshop's implementation)
    x_d65 = x * 0.9555766 + y * -0.0230393 + z * 0.0631636
    y_d65 = x * -0.0282895 + y * 1.0099416 + z * 0.0210077
    z_d65 = x * 0.0122982 + y * -0.0204830 + z * 1.3299098
    
    # RGB D65 matrix (from Photoshop's implementation)
    r = x_d65 *  3.2409699419045226 - y_d65 * 1.5373831775700935 - z_d65 * 0.4986107602930034
    g = x_d65 * -0.9692436362808796 + y_d65 * 1.8759675015077204 + z_d65 * 0.0415550574071756
    b = x_d65 *  0.0556300796969936 - y_d65 * 0.2039769588889765 + z_d65 * 1.0569715142428784
    
    def to_srgb(c):
        # Allow slightly out-of-range values before clamping (Photoshop behavior)
        if abs(c) < 0.0001:  # Handle near-zero values
            return 0
            
        if c <= 0.0031308:
            c = c * 12.92
        else:
            c = 1.055 * pow(abs(c), 1/2.4) - 0.055
            
        # Final clamping with small tolerance
        return max(0.0, min(1.0, c))
    
    r = to_srgb(r)
    g = to_srgb(g)
    b = to_srgb(b)
    
    return (r, g, b)

def rgb_to_xyz(rgb):
    """Convert from sRGB to XYZ D50"""
    r, g, b = rgb
    
    # sRGB to linear RGB
    def to_linear(c):
        c = max(0, min(1, c))
        if c <= 0.04045:
            return c / 12.92
        return pow((c + 0.055) / 1.055, 2.4)
    
    r = to_linear(r)
    g = to_linear(g)
    b = to_linear(b)
    
    # Linear RGB to XYZ D65
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    
    # Bradford transformation from D65 to D50
    x_d50 = x * 1.0478112 + y * 0.0228866 + z * -0.0501270
    y_d50 = x * 0.0295424 + y * 0.9904844 + z * -0.0170491
    z_d50 = x * -0.0092345 + y * 0.0150436 + z * 0.7521316
    
    return (x_d50, y_d50, z_d50)


def rgb_to_lab(rgb):
    """Convert RGB to LAB"""
    xyz = rgb_to_xyz(rgb)
    return xyz_to_lab(xyz)

def lab_to_rgb(lab):
    """Convert from LAB to RGB with additional handling for extreme values"""
    L, a, b = lab
    
    # Special handling for extreme LAB values
    if L < 0.01:  # For near-zero L values
        if abs(a) > 127 or abs(b) > 127:  # Extreme a/b values
            # Use more precise conversion for these edge cases
            xyz = lab_to_xyz((L, max(-128, min(127, a)), max(-128, min(127, b))))
            rgb = xyz_to_rgb(xyz)
            # Apply Photoshop-like gamma correction for extreme values
            return tuple(max(0, min(1, c)) for c in rgb)
    
    # Normal conversion for other values
    xyz = lab_to_xyz(lab)
    return xyz_to_rgb(xyz)

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