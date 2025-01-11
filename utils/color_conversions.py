def rgb_to_xyz_d50(rgb):
    """Convert from sRGB to XYZ D50"""
    # First convert to XYZ D65
    r, g, b = rgb
    
    def to_linear(c):
        c = max(0, min(1, c))
        if c <= 0.04045:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4
    
    r = to_linear(r)
    g = to_linear(g)
    b = to_linear(b)
    
    # sRGB D65 to XYZ D65
    x = r * 0.4124564390896922 + g * 0.357576077643909 + b * 0.18043748326639894
    y = r * 0.21267285140562253 + g * 0.715152155287818 + b * 0.07217499330655958
    z = r * 0.019333895582329317 + g * 0.119192025881303 + b * 0.9503040785363677
    
    # Bradford transformation matrix from D65 to D50
    # Values from http://www.brucelindbloom.com/index.html?Eqn_ChromAdapt.html
    x_d50 = x * 1.0478112 + y * 0.0228866 + z * -0.0501270
    y_d50 = x * 0.0295424 + y * 0.9904844 + z * -0.0170491
    z_d50 = x * -0.0092345 + y * 0.0150436 + z * 0.7521316
    
    return (x_d50, y_d50, z_d50)

def xyz_to_lab(xyz):
    x, y, z = xyz
    
    # D50 white point values
    ref_x = 0.96422
    ref_y = 1.00000
    ref_z = 0.82521
    
    # Photoshop's thresholds
    epsilon = 216.0 / 24389.0  # ≈ 0.008856
    kappa = 24389.0 / 27.0     # ≈ 903.3
    
    def f(t):
        if t > epsilon:
            return t ** (1.0/3.0)
        return (kappa * t + 16) / 116.0
    
    xr = x / ref_x
    yr = y / ref_y
    zr = z / ref_z
    
    fx = f(xr)
    fy = f(yr)
    fz = f(zr)
    
    L = max(0.0, min(100.0, (116.0 * fy) - 16.0))
    a = max(-128.0, min(127.0, 500.0 * (fx - fy)))
    b = max(-128.0, min(127.0, 200.0 * (fy - fz)))
    
    return (L, a, b)

def lab_to_xyz(lab):
    L, a, b = lab
    
    # D50 white point values
    ref_x = 0.96422
    ref_y = 1.00000
    ref_z = 0.82521
    
    epsilon = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    
    fy = (L + 16.0) / 116.0
    fx = fy + (a / 500.0)
    fz = fy - (b / 200.0)
    
    def f_inv(t):
        t3 = t ** 3
        if t3 > epsilon:
            return t3
        return (116.0 * t - 16.0) / kappa
    
    x = ref_x * f_inv(fx)
    y = ref_y * f_inv(fy) if L > (kappa * epsilon) else (L * ref_y) / kappa
    z = ref_z * f_inv(fz)
    
    return (x, y, z)

def xyz_to_rgb(xyz):
    """Convert from XYZ D50 to sRGB"""
    x, y, z = xyz
    
    # Bradford transformation matrix from D50 to D65
    x_d65 = x * 0.9555766 + y * -0.0230393 + z * 0.0631636
    y_d65 = x * -0.0282895 + y * 1.0099416 + z * 0.0210077
    z_d65 = x * 0.0122982 + y * -0.0204830 + z * 1.3299098
    
    # XYZ D65 to linear RGB
    r = x_d65 * 3.2404542361650636 - y_d65 * 1.5371385127253755 - z_d65 * 0.4985314095560162
    g = x_d65 * -0.9692660305051868 + y_d65 * 1.8760108454466942 + z_d65 * 0.0415560007378110
    b = x_d65 * 0.0556434318254943 - y_d65 * 0.2040259135167538 + z_d65 * 1.0572251882231787
    
    def to_srgb(c):
        if c <= 0.0031308:
            return max(0, min(1, 12.92 * c))
        return max(0, min(1, 1.055 * (abs(c) ** (1/2.4)) - 0.055))
    
    r = to_srgb(r)
    g = to_srgb(g)
    b = to_srgb(b)
    
    return (
        max(0, min(1, r)),
        max(0, min(1, g)),
        max(0, min(1, b))
    )

def rgb_to_lab(rgb):
    """Convert from RGB to LAB using D50 white point"""
    xyz = rgb_to_xyz_d50(rgb)
    return xyz_to_lab(xyz)

def lab_to_rgb(lab):
    """Convert from LAB to RGB using D50 white point"""
    xyz = lab_to_xyz(lab)
    return xyz_to_rgb(xyz)

# Helper function to convert RGB to hex
def rgb_to_hex(rgb):
    """Convert RGB (0-1) values to hex string"""
    return "#{:02x}{:02x}{:02x}".format(
        int(rgb[0] * 255),
        int(rgb[1] * 255),
        int(rgb[2] * 255)
    )

# Test function
def run_tests():
    test_cases = [
        # Pure blue test from Stack Overflow
        {"rgb": (0, 0, 1), "expected_lab": (30, 68, -112)},  # D50 values
        
        # Original test cases
        {"lab": (0, -128, -128), "expected_rgb": "#001ECC"},
        {"lab": (100, -128, -128), "expected_rgb": "#00FFFF"},
        {"lab": (0, 128, -128), "expected_rgb": "#FF0000"},
        {"lab": (50, 0, 0), "expected_rgb": "#777777"},
    ]
    
    print("Running conversion tests...")
    print("-" * 50)
    
    # Test RGB -> LAB
    rgb_test = (0, 0, 1)  # Pure blue
    lab_result = rgb_to_lab(rgb_test)
    print(f"Pure blue RGB {rgb_test} -> LAB {lab_result}")
    print(f"Expected LAB values for D50: (30, 68, -112)")
    
    # Test other cases
    for test in test_cases:
        if "lab" in test:
            lab = test["lab"]
            rgb = lab_to_rgb(lab)
            hex_color = rgb_to_hex(rgb)
            print(f"\nLAB {lab} -> {hex_color} (Expected: {test['expected_rgb']})")
            
            # Test reverse conversion
            rgb_decimal = tuple(int(hex_color[i:i+2], 16)/255 for i in (1,3,5))
            lab_result = rgb_to_lab(rgb_decimal)
            print(f"RGB {rgb_decimal} -> LAB {lab_result}")

if __name__ == "__main__":
    run_tests()