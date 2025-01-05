def rgb_to_xyz(rgb):
    r, g, b = rgb
    
    # sRGB to linear RGB
    def to_linear(c):
        if c > 0.04045:
            return ((c + 0.055) / 1.055) ** 2.4
        return c / 12.92
    
    r = to_linear(r)
    g = to_linear(g)
    b = to_linear(b)
    
    # Linear RGB to XYZ using D65 white point
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    
    return (x, y, z)

def xyz_to_lab(xyz):
    x, y, z = xyz
    # D65 white point
    ref_x, ref_y, ref_z = 0.95047, 1.0, 1.08883
    
    # XYZ to relative XYZ
    x = x / ref_x
    y = y / ref_y
    z = z / ref_z
    
    # Relative XYZ to Lab
    epsilon = 0.008856
    kappa = 903.3
    
    def f(t):
        if t > epsilon:
            return t ** (1/3)
        return (kappa * t + 16) / 116

    fx = f(x)
    fy = f(y)
    fz = f(z)
    
    L = max(0, min(100, 116 * fy - 16))
    a = max(-128, min(127, 500 * (fx - fy)))
    b = max(-128, min(127, 200 * (fy - fz)))
    
    return (L, a, b)

def lab_to_xyz(lab):
    L, a, b = lab
    
    # D65 white point
    ref_x, ref_y, ref_z = 0.95047, 1.0, 1.08883
    
    epsilon = 0.008856
    kappa = 903.3
    
    fy = (L + 16) / 116
    fx = fy + (a / 500)
    fz = fy - (b / 200)
    
    def f_inv(t):
        t3 = t ** 3
        if t3 > epsilon:
            return t3
        return (116 * t - 16) / kappa
    
    x = ref_x * f_inv(fx)
    y = ref_y * f_inv(fy)
    z = ref_z * f_inv(fz)
    
    return (x, y, z)

def xyz_to_rgb(xyz):
    x, y, z = xyz
    
    # XYZ to linear RGB
    r = x * 3.2404542 - y * 1.5371385 - z * 0.4985314
    g = -x * 0.9692660 + y * 1.8760108 + z * 0.0415560
    b = x * 0.0556434 - y * 0.2040259 + z * 1.0572252
    
    # Linear RGB to sRGB
    def to_srgb(c):
        if c <= 0.0031308:
            return max(0, min(1, 12.92 * c))
        return max(0, min(1, 1.055 * (c ** (1/2.4)) - 0.055))
    
    r = to_srgb(r)
    g = to_srgb(g)
    b = to_srgb(b)
    
    return (r, g, b)

# Add these two new functions:
def rgb_to_lab(rgb):
    """Convert from RGB to LAB directly"""
    xyz = rgb_to_xyz(rgb)
    return xyz_to_lab(xyz)

def lab_to_rgb(lab):
    """Convert from LAB to RGB directly"""
    xyz = lab_to_xyz(lab)
    return xyz_to_rgb(xyz)

# Don't forget to add them to __all__
__all__ = [
    'rgb_to_xyz',
    'xyz_to_lab',
    'lab_to_xyz',
    'xyz_to_rgb',
    'rgb_to_lab',  # new
    'lab_to_rgb'   # new
]