import bpy
import numpy as np
from math import pow

"""
Color space conversion utilities for Blender 5.0+
Handles scene linear ↔ sRGB conversions for proper color management.
"""

def rgb_to_hex(rgb_float):
    """Convert RGB float values to hex string"""
    rgb_bytes = rgb_float_to_bytes(rgb_float)
    return "#{:02X}{:02X}{:02X}".format(*rgb_bytes)

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

def rgb_bytes_to_float(rgb_bytes):
    """Convert RGB bytes (0-255) to float values (0-1)"""
    return tuple(c / 255 for c in rgb_bytes)

def rgb_float_to_bytes(rgb_float):
    """Convert RGB float values (0-1) to bytes (0-255)"""
    return tuple(round(c * 255) for c in rgb_float)

def srgb_to_linear(c):
    """
    Convert single sRGB channel to scene linear color space.
    
    Args:
        c: Color channel value in sRGB space [0.0, 1.0]
    
    Returns:
        float: Color channel in scene linear space [0.0, 1.0]
    """
    c = max(0.0, min(1.0, c))
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c):
    """
    Convert single scene linear channel to sRGB color space.
    
    Args:
        c: Color channel value in scene linear space [0.0, 1.0]
    
    Returns:
        float: Color channel in sRGB space [0.0, 1.0]
    """
    c = max(0.0, min(1.0, c))
    if c <= 0.0031308:
        return c * 12.92
    return 1.055 * (c ** (1.0 / 2.4)) - 0.055


def rgb_srgb_to_linear(rgb_srgb):
    """
    Convert RGB tuple from sRGB to scene linear color space.
    
    Args:
        rgb_srgb: Tuple of (r, g, b) in sRGB space [0.0, 1.0]
    
    Returns:
        tuple: (r, g, b) in scene linear space [0.0, 1.0]
    """
    return tuple(srgb_to_linear(c) for c in rgb_srgb[:3])


def rgb_linear_to_srgb(rgb_linear):
    """
    Convert RGB tuple from scene linear to sRGB color space.
    
    Args:
        rgb_linear: Tuple of (r, g, b) in scene linear space [0.0, 1.0]
    
    Returns:
        tuple: (r, g, b) in sRGB space [0.0, 1.0]
    """
    return tuple(linear_to_srgb(c) for c in rgb_linear[:3])


def rgb_bytes_to_linear(rgb_bytes):
    """
    Convert RGB bytes (0-255) to scene linear float values.
    
    Args:
        rgb_bytes: Tuple of (r, g, b) in range [0, 255] (sRGB assumed)
    
    Returns:
        tuple: (r, g, b) in scene linear space [0.0, 1.0]
    """
    rgb_srgb = tuple(c / 255.0 for c in rgb_bytes)
    return rgb_srgb_to_linear(rgb_srgb)


def rgb_linear_to_bytes(rgb_linear):
    """
    Convert scene linear RGB to bytes (0-255) in sRGB space.
    
    Args:
        rgb_linear: Tuple of (r, g, b) in scene linear space [0.0, 1.0]
    
    Returns:
        tuple: (r, g, b) as integers in range [0, 255] (sRGB)
    """
    rgb_srgb = rgb_linear_to_srgb(rgb_linear)
    return tuple(round(c * 255) for c in rgb_srgb)


def hex_to_linear(hex_str):
    """
    Convert hex color string to scene linear RGB.
    
    Args:
        hex_str: Hex color string (e.g., "#FF0000" or "FF0000")
    
    Returns:
        tuple: (r, g, b) in scene linear space [0.0, 1.0]
    """
    hex_str = hex_str.lstrip('#')
    if len(hex_str) != 6:
        return (0.0, 0.0, 0.0)
    
    try:
        rgb_bytes = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return rgb_bytes_to_linear(rgb_bytes)
    except ValueError:
        return (0.0, 0.0, 0.0)


def linear_to_hex(rgb_linear):
    """
    Convert scene linear RGB to hex color string.
    
    Args:
        rgb_linear: Tuple of (r, g, b) in scene linear space [0.0, 1.0]
    
    Returns:
        str: Hex color string (e.g., "#FF0000")
    """
    rgb_bytes = rgb_linear_to_bytes(rgb_linear)
    return "#{:02X}{:02X}{:02X}".format(*rgb_bytes)


__all__ = [
    'srgb_to_linear',
    'linear_to_srgb',
    'rgb_srgb_to_linear',
    'rgb_linear_to_srgb',
    'rgb_bytes_to_linear',
    'rgb_linear_to_bytes',
    'hex_to_linear',
    'linear_to_hex'
]
