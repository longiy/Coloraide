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
    
    # Linear RGB to XYZ
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    
    return (x, y, z)

def xyz_to_lab(xyz):
    x, y, z = xyz
    # D65 illuminant
    ref_x, ref_y, ref_z = 0.95047, 1.0, 1.08883
    
    x = x / ref_x
    y = y / ref_y
    z = z / ref_z
    
    def f(t):
        delta = 6.0 / 29.0
        if t > delta ** 3:
            return t ** (1.0 / 3.0)
        return t / (3.0 * delta ** 2) + 4.0 / 29.0
    
    fx = f(x)
    fy = f(y)
    fz = f(z)
    
    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    
    return (L, a, b)

def lab_to_xyz(lab):
    L, a, b = lab
    # D65 illuminant
    ref_x, ref_y, ref_z = 0.95047, 1.0, 1.08883
    
    fy = (L + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0
    
    def f_inv(t):
        delta = 6.0 / 29.0
        if t > delta:
            return t ** 3
        return 3 * delta ** 2 * (t - 4.0 / 29.0)
    
    x = ref_x * f_inv(fx)
    y = ref_y * f_inv(fy)
    z = ref_z * f_inv(fz)
    
    return (x, y, z)

def xyz_to_rgb(xyz):
    x, y, z = xyz
    # XYZ to linear RGB
    r = x *  3.2404542 + y * -1.5371385 + z * -0.4985314
    g = x * -0.9692660 + y *  1.8760108 + z *  0.0415560
    b = x *  0.0556434 + y * -0.2040259 + z *  1.0572252
    
    # Linear RGB to sRGB
    def to_srgb(c):
        if c > 0.0031308:
            return 1.055 * (c ** (1.0 / 2.4)) - 0.055
        return 12.92 * c
    
    r = to_srgb(r)
    g = to_srgb(g)
    b = to_srgb(b)
    
    # Clamp values
    r = max(0, min(1, r))
    g = max(0, min(1, g))
    b = max(0, min(1, b))
    
    return (r, g, b)

def rgb_to_lab(rgb):
    xyz = rgb_to_xyz(rgb)
    return xyz_to_lab(xyz)

def lab_to_rgb(lab):
    xyz = lab_to_xyz(lab)
    return xyz_to_rgb(xyz)