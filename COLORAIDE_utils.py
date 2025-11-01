"""
Utility functions for Coloraide addon - Blender 5.0+ version.
All color conversion functions work with scene linear RGB as input/output.
"""

import numpy as np
from math import pow
from .COLORAIDE_colorspace import *

def rgb_to_hsv(rgb_linear):
    """
    Convert scene linear RGB to HSV.
    
    Args:
        rgb_linear: Tuple of (r, g, b) in scene linear space [0.0, 1.0]
    
    Returns:
        tuple: (h, s, v) where h is [0.0, 1.0], s is [0.0, 1.0], v is [0.0, 1.0]
    """
    r, g, b = rgb_linear
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
    """
    Convert HSV to scene linear RGB.
    
    Args:
        hsv: Tuple of (h, s, v) where h is [0.0, 1.0], s is [0.0, 1.0], v is [0.0, 1.0]
    
    Returns:
        tuple: (r, g, b) in scene linear space [0.0, 1.0]
    """
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


def rgb_to_xyz(rgb_linear):
    """
    Convert scene linear RGB to XYZ color space (D50).
    
    Args:
        rgb_linear: Tuple of (r, g, b) in scene linear space [0.0, 1.0]
    
    Returns:
        tuple: (x, y, z) in XYZ D50 color space
    """
    r, g, b = rgb_linear
    
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
    """
    Convert XYZ D50 to LAB color space.
    
    Args:
        xyz: Tuple of (x, y, z) in XYZ D50 color space
    
    Returns:
        tuple: (L, a, b) where L is [0, 100], a is [-128, 127], b is [-128, 127]
    """
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


def lab_to_xyz(lab):
    """
    Convert LAB to XYZ D50 color space.
    
    Args:
        lab: Tuple of (L, a, b) where L is [0, 100], a is [-128, 127], b is [-128, 127]
    
    Returns:
        tuple: (x, y, z) in XYZ D50 color space
    """
    L, a, b = lab
    
    # ICC constants
    epsilon = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    
    # D50 reference white
    ref_x = 0.96422
    ref_y = 1.00000
    ref_z = 0.82521
    
    # Special handling for L=0
    if L < 0.01:
        fy = 16.0 / 116.0
    else:
        fy = (L + 16.0) / 116.0
    
    fx = fy + (a / 500.0)
    fz = fy - (b / 200.0)
    
    # Modified f_inv function
    def f_inv(t):
        t3 = t * t * t
        if t > 6.0/29.0:
            return t3
        return (116.0 * t - 16.0) / kappa
    
    x = ref_x * f_inv(fx)
    y = ref_y * f_inv(fy)
    z = ref_z * f_inv(fz)
    
    # Clamp to valid range
    x = max(0, x)
    y = max(0, y)
    z = max(0, z)
    
    return (x, y, z)


def xyz_to_rgb(xyz):
    """
    Convert XYZ D50 to scene linear RGB.
    
    Args:
        xyz: Tuple of (x, y, z) in XYZ D50 color space
    
    Returns:
        tuple: (r, g, b) in scene linear space [0.0, 1.0]
    """
    x, y, z = xyz
    
    # Bradford matrix D50 -> D65
    x_d65 = x * 0.9555766 + y * -0.0230393 + z * 0.0631636
    y_d65 = x * -0.0282895 + y * 1.0099416 + z * 0.0210077
    z_d65 = x * 0.0122982 + y * -0.0204830 + z * 1.3299098
    
    # RGB D65 matrix
    r = x_d65 *  3.2409699419045226 - y_d65 * 1.5373831775700935 - z_d65 * 0.4986107602930034
    g = x_d65 * -0.9692436362808796 + y_d65 * 1.8759675015077204 + z_d65 * 0.0415550574071756
    b = x_d65 *  0.0556300796969936 - y_d65 * 0.2039769588889765 + z_d65 * 1.0569715142428784
    
    # Clamp to valid range (already linear, no conversion needed)
    r = max(0.0, min(1.0, r))
    g = max(0.0, min(1.0, g))
    b = max(0.0, min(1.0, b))
    
    return (r, g, b)


def rgb_to_lab(rgb_linear):
    """
    Convert scene linear RGB to LAB.
    
    Args:
        rgb_linear: Tuple of (r, g, b) in scene linear space [0.0, 1.0]
    
    Returns:
        tuple: (L, a, b) where L is [0, 100], a is [-128, 127], b is [-128, 127]
    """
    xyz = rgb_to_xyz(rgb_linear)
    return xyz_to_lab(xyz)


def lab_to_rgb(lab):
    """
    Convert LAB to scene linear RGB.
    
    Args:
        lab: Tuple of (L, a, b) where L is [0, 100], a is [-128, 127], b is [-128, 127]
    
    Returns:
        tuple: (r, g, b) in scene linear space [0.0, 1.0]
    """
    xyz = lab_to_xyz(lab)
    return xyz_to_rgb(xyz)


def color_statistics(colors):
    """
    Calculate color statistics for an array of colors.
    
    Args:
        colors: numpy array of colors in scene linear space
    
    Returns:
        dict: Statistics including mean, median, min, max
    """
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


__all__ = [
    'rgb_to_hsv',
    'hsv_to_rgb',
    'rgb_to_lab',
    'lab_to_rgb',
    'rgb_to_xyz',
    'xyz_to_rgb',
    'xyz_to_lab',
    'lab_to_xyz',
    'color_statistics'
]
