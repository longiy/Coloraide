"""
Cross-platform screen pixel sampling for Coloraide color picker.

Strategy per platform:
  macOS  — CoreGraphics CGWindowListCreateImage via ctypes.
            Reads the fully composited Metal display buffer.
            Requires Screen Recording permission (System Settings → Privacy & Security).
  Windows — GDI32 BitBlt via ctypes.
            Reads the composited GDI display buffer. No special permissions needed.
  Linux  — Returns None; caller falls back to GPU framebuffer in a draw callback.
"""

import sys
import time
import ctypes
import numpy as np

# Minimum seconds between screen-capture samples (~60 fps cap).
# CGWindowListCreateImage / BitBlt each take ~10-30 ms; without this cap
# high-frequency MOUSEMOVE events queue up and make the picker feel laggy.
_SAMPLE_INTERVAL = 1.0 / 60.0
_last_sample_time: float = 0.0

# ---------------------------------------------------------------------------
# macOS — CoreGraphics
# ---------------------------------------------------------------------------

_cg = None
_cf = None
_macos_ok = None


def _load_macos():
    global _cg, _cf, _macos_ok
    if _macos_ok is not None:
        return _macos_ok
    try:
        _cg = ctypes.CDLL('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
        _cf = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')

        # Configure function signatures once so the hot path doesn't repeat this work.
        _cg.CGEventCreate.restype = ctypes.c_void_p
        _cg.CGEventCreate.argtypes = [ctypes.c_void_p]
        _cg.CGEventGetLocation.restype = _CGPoint
        _cg.CGEventGetLocation.argtypes = [ctypes.c_void_p]
        _cg.CGWindowListCreateImage.restype = ctypes.c_void_p
        _cg.CGWindowListCreateImage.argtypes = [_CGRect, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        _cg.CGImageGetWidth.restype = ctypes.c_size_t
        _cg.CGImageGetWidth.argtypes = [ctypes.c_void_p]
        _cg.CGImageGetHeight.restype = ctypes.c_size_t
        _cg.CGImageGetHeight.argtypes = [ctypes.c_void_p]
        _cg.CGImageGetBytesPerRow.restype = ctypes.c_size_t
        _cg.CGImageGetBytesPerRow.argtypes = [ctypes.c_void_p]
        _cg.CGImageGetBitsPerPixel.restype = ctypes.c_size_t
        _cg.CGImageGetBitsPerPixel.argtypes = [ctypes.c_void_p]
        _cg.CGImageGetDataProvider.restype = ctypes.c_void_p
        _cg.CGImageGetDataProvider.argtypes = [ctypes.c_void_p]
        _cg.CGDataProviderCopyData.restype = ctypes.c_void_p
        _cg.CGDataProviderCopyData.argtypes = [ctypes.c_void_p]
        _cg.CGImageRelease.restype = None
        _cg.CGImageRelease.argtypes = [ctypes.c_void_p]
        _cf.CFDataGetLength.restype = ctypes.c_long
        _cf.CFDataGetLength.argtypes = [ctypes.c_void_p]
        _cf.CFDataGetBytePtr.restype = ctypes.c_void_p
        _cf.CFDataGetBytePtr.argtypes = [ctypes.c_void_p]
        _cf.CFRelease.restype = None
        _cf.CFRelease.argtypes = [ctypes.c_void_p]

        _macos_ok = True
    except Exception as e:
        print(f"[CPICKER screen] CoreGraphics load failed: {e}")
        _macos_ok = False
    return _macos_ok


class _CGPoint(ctypes.Structure):
    _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double)]

class _CGSize(ctypes.Structure):
    _fields_ = [('width', ctypes.c_double), ('height', ctypes.c_double)]

class _CGRect(ctypes.Structure):
    _fields_ = [('origin', _CGPoint), ('size', _CGSize)]


def _cursor_macos():
    if not _load_macos():
        return None
    ev = _cg.CGEventCreate(None)
    if not ev:
        return None
    pos = _cg.CGEventGetLocation(ev)
    _cf.CFRelease(ev)
    return (pos.x, pos.y)


def _sample_macos(sqrt_size):
    if not _load_macos():
        return None, None, None
    pos = _cursor_macos()
    if pos is None:
        return None, None, None
    cx, cy = pos
    half = sqrt_size // 2
    try:
        _cg.CGWindowListCreateImage.restype = ctypes.c_void_p
        _cg.CGWindowListCreateImage.argtypes = [_CGRect, ctypes.c_uint32,
                                                ctypes.c_uint32, ctypes.c_uint32]
        rect = _CGRect(_CGPoint(cx - half, cy - half), _CGSize(sqrt_size, sqrt_size))
        img = _cg.CGWindowListCreateImage(rect,
                                          ctypes.c_uint32(1),   # kCGWindowListOptionOnScreenOnly
                                          ctypes.c_uint32(0),   # kCGNullWindowID
                                          ctypes.c_uint32(0))   # kCGWindowImageDefault
        if not img:
            print(f"[CPICKER screen/macOS] CGWindowListCreateImage NULL — "
                  f"check Screen Recording permission in System Settings")
            return None, None, None

        img_w = _cg.CGImageGetWidth(img)
        img_h = _cg.CGImageGetHeight(img)
        bpr   = _cg.CGImageGetBytesPerRow(img)
        bpp   = _cg.CGImageGetBitsPerPixel(img) // 8

        provider = _cg.CGImageGetDataProvider(img)
        data_ref = _cg.CGDataProviderCopyData(provider)
        if not data_ref:
            _cg.CGImageRelease(img)
            return None, None, None

        length = _cf.CFDataGetLength(data_ref)
        ptr    = _cf.CFDataGetBytePtr(data_ref)
        raw    = (ctypes.c_uint8 * length).from_address(ptr)
        buf    = np.frombuffer(bytes(raw), dtype=np.uint8).copy()
        _cf.CFRelease(data_ref)
        _cg.CGImageRelease(img)

        rows = min(img_h, length // bpr)
        pixels = buf[:rows * bpr].reshape(rows, bpr)[:, :img_w * bpp].reshape(rows, img_w, bpp)

        # CoreGraphics BGRA → RGB
        r_ch = pixels[:, :, 2].astype(np.float32) / 255.0
        g_ch = pixels[:, :, 1].astype(np.float32) / 255.0
        b_ch = pixels[:, :, 0].astype(np.float32) / 255.0
        channels = np.stack([r_ch, g_ch, b_ch], axis=2).reshape(-1, 3)

        mean_srgb = tuple(np.mean(channels, axis=0))
        cy_i = rows // 2
        cx_i = img_w // 2
        c = pixels[cy_i, cx_i]
        curr_srgb = (c[2] / 255.0, c[1] / 255.0, c[0] / 255.0)
        return channels, mean_srgb, curr_srgb

    except Exception as e:
        print(f"[CPICKER screen/macOS] sample failed: {e}")
        import traceback; traceback.print_exc()
        return None, None, None


# ---------------------------------------------------------------------------
# Windows — GDI32
# ---------------------------------------------------------------------------

_win_dbg_counter = 0
_WIN_DBG_EVERY = 15

def _sample_windows(sqrt_size):
    global _win_dbg_counter
    _win_dbg_counter += 1
    dbg = (_win_dbg_counter % _WIN_DBG_EVERY == 1)

    try:
        user32 = ctypes.windll.user32
        gdi32  = ctypes.windll.gdi32

        # Cursor position
        class POINT(ctypes.Structure):
            _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        cx, cy = pt.x, pt.y

        x = cx - sqrt_size // 2
        y = cy - sqrt_size // 2

        if dbg:
            print(f"[CPICKER win] cursor=({cx},{cy})  capture=({x},{y},{sqrt_size}x{sqrt_size})")

        # Capture via BitBlt into a memory DC
        hdc_screen = user32.GetDC(None)
        hdc_mem    = gdi32.CreateCompatibleDC(hdc_screen)
        hbmp       = gdi32.CreateCompatibleBitmap(hdc_screen, sqrt_size, sqrt_size)
        gdi32.SelectObject(hdc_mem, hbmp)
        SRCCOPY = 0x00CC0020
        gdi32.BitBlt(hdc_mem, 0, 0, sqrt_size, sqrt_size, hdc_screen, x, y, SRCCOPY)

        # Read pixels with GetDIBits (BGRA, top-down)
        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ('biSize',          ctypes.c_uint32),
                ('biWidth',         ctypes.c_int32),
                ('biHeight',        ctypes.c_int32),
                ('biPlanes',        ctypes.c_uint16),
                ('biBitCount',      ctypes.c_uint16),
                ('biCompression',   ctypes.c_uint32),
                ('biSizeImage',     ctypes.c_uint32),
                ('biXPelsPerMeter', ctypes.c_int32),
                ('biYPelsPerMeter', ctypes.c_int32),
                ('biClrUsed',       ctypes.c_uint32),
                ('biClrImportant',  ctypes.c_uint32),
            ]
        bmi            = BITMAPINFOHEADER()
        bmi.biSize     = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth    = sqrt_size
        bmi.biHeight   = -sqrt_size   # negative = top-down
        bmi.biPlanes   = 1
        bmi.biBitCount = 32
        buf_size = sqrt_size * sqrt_size * 4
        buf = (ctypes.c_uint8 * buf_size)()
        DIB_RGB_COLORS = 0
        gdi32.GetDIBits(hdc_mem, hbmp, 0, sqrt_size, buf,
                        ctypes.byref(bmi), DIB_RGB_COLORS)

        user32.ReleaseDC(None, hdc_screen)
        gdi32.DeleteDC(hdc_mem)
        gdi32.DeleteObject(hbmp)

        pixels = np.frombuffer(buf, dtype=np.uint8).copy().reshape(sqrt_size, sqrt_size, 4)

        mid = sqrt_size // 2
        c_raw = pixels[mid, mid]   # centre pixel raw bytes

        if dbg:
            print(f"[CPICKER win] buf_size={buf_size}  pixels.shape={pixels.shape}")
            print(f"  centre pixel raw BGRA bytes: {list(c_raw)}")
            # Sample a few corners to understand channel order
            corners = {
                'tl': pixels[0,           0          ],
                'tr': pixels[0,           sqrt_size-1],
                'bl': pixels[sqrt_size-1, 0          ],
                'br': pixels[sqrt_size-1, sqrt_size-1],
                'mid': c_raw,
            }
            for name, px in corners.items():
                print(f"  {name}: raw={list(px)}  "
                      f"as_BGRA=B{px[0]} G{px[1]} R{px[2]} A{px[3]}  "
                      f"as_RGB=({px[2]/255:.3f},{px[1]/255:.3f},{px[0]/255:.3f})")

        # GDI GetDIBits with BI_RGB returns BGR(X) — channel 0=B, 1=G, 2=R, 3=padding
        r_ch = pixels[:, :, 2].astype(np.float32) / 255.0
        g_ch = pixels[:, :, 1].astype(np.float32) / 255.0
        b_ch = pixels[:, :, 0].astype(np.float32) / 255.0
        channels = np.stack([r_ch, g_ch, b_ch], axis=2).reshape(-1, 3)

        mean_srgb = tuple(np.mean(channels, axis=0))
        curr_srgb = (c_raw[2] / 255.0, c_raw[1] / 255.0, c_raw[0] / 255.0)

        if dbg:
            spread = max(mean_srgb) - min(mean_srgb)
            print(f"  mean_srgb=({mean_srgb[0]:.3f},{mean_srgb[1]:.3f},{mean_srgb[2]:.3f})"
                  f"  curr_srgb=({curr_srgb[0]:.3f},{curr_srgb[1]:.3f},{curr_srgb[2]:.3f})"
                  f"  spread={spread:.4f}{'  *** GREY' if spread < 0.01 else '  OK'}")
            # Also print a few random pixel values to check for variety
            sample_idxs = [(0,0),(0,sqrt_size//2),(sqrt_size//2,0),(sqrt_size//2,sqrt_size//2)]
            print("  pixel samples (RGB):", [
                f"({pixels[r,c,2]/255:.2f},{pixels[r,c,1]/255:.2f},{pixels[r,c,0]/255:.2f})"
                for r,c in sample_idxs if r < sqrt_size and c < sqrt_size
            ])

        return channels, mean_srgb, curr_srgb

    except Exception as e:
        print(f"[CPICKER screen/Windows] sample failed: {e}")
        import traceback; traceback.print_exc()
        return None, None, None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_native_capture_available():
    """True on macOS and Windows where OS-level screen capture is used."""
    return sys.platform in ('darwin', 'win32')


def sample_at_cursor(sqrt_size):
    """
    Capture sqrt_size×sqrt_size pixels centred on the current cursor.
    Returns (channels_srgb, mean_srgb, curr_srgb) — floats in [0,1] sRGB —
    or (None, None, None) if unavailable or throttled.
    """
    global _last_sample_time
    now = time.monotonic()
    if now - _last_sample_time < _SAMPLE_INTERVAL:
        return None, None, None
    _last_sample_time = now

    if sys.platform == 'darwin':
        return _sample_macos(sqrt_size)
    elif sys.platform == 'win32':
        return _sample_windows(sqrt_size)
    else:
        return None, None, None   # Linux: GPU framebuffer fallback in CPICKER_OT
