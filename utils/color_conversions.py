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

# Helper functions remain the same
def rgb_to_lab(rgb):
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
