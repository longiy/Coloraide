# 🎨 Coloraide
Advanced color picker and manager for Blender 4.3+
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/Coloraide_Preview.png)
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/Coloraide_Preview2.png)

## ✨ Features
🔍 Quick Pick (Shift+E)
Real-time screen color sampling activated by holding Shift+E. Customizable sample area from 1-100 pixels displays both area average and single-pixel color with visual preview during sampling.
# 🎯 Normal Sampling
Converts 3D mesh surface normals into RGB colors for normal map workflows. Supports both smooth and flat shading with world-space normal sampling in Texture Paint and Vertex Paint modes.
# 🎡 Color Wheel
Visual hue/saturation selector with integrated value slider. Scalable size (1.0-3.0x multiplier) for precision work, includes hex input field and reset-to-default button.
# 🌈 Color Spaces
Multiple color representations updated in real-time: RGB (0-255 bytes), HSV (360° hue, 0-100% sat/val), LAB (perceptually uniform), and Hex (#RRGGBB). All conversions maintain Photoshop-level accuracy using scene linear color space internally.
# 📋 History
Automatically stores recently used colors in an adjustable grid (8-80 slots, 8 per row). Click any swatch to instantly reapply that color, with automatic duplicate prevention and clear-all option.
# 🎨 Palettes
Seamless integration with Blender's native palette system. Add current color to palette, select from swatches, and manage persistent color collections that save with .blend files.
# 🖌️ Color Dynamics
Native brush color jitter control (Blender 5.0+) for hue, saturation, and value randomization. Includes per-stroke variation, pressure sensitivity, and customizable pressure curves for natural painting variation.
# 🔧 Compatibility
Version Requirements

Version 1.4.8: Requires Blender 4.5 or newer for full feature support
Version 1.4.7: Compatible with Blender 4.5 and earlier versions

# Supported Editors

Image Editor: Texture painting and 2D paint workflows
3D View: Texture Paint, Vertex Paint, Sculpt, Grease Pencil modes
Clip Editor: Motion tracking and rotoscoping with color tools

Paint Modes
Works across all Blender paint modes including Texture Paint, Vertex Paint, Weight Paint, Sculpt, Grease Pencil Draw, and Vertex Grease Pencil.
⌨️ Controls
Keyboard Shortcuts

Quick Pick: Shift+E - Press and hold to sample, release to confirm

Panel Controls

Color Spaces: Toggle RGB/HSV/LAB buttons in Color Sliders section to show/hide
History Size: Use +/- buttons to adjust between 8-80 color slots
Wheel Scale: Drag slider (1.0-3.0x) or click reset button (↻) to restore default (1.5x)
Panel Location: Customizable in Preferences → Add-ons → Coloraide → Tab Category

📦 Info

Version: 1.4.8
Author: longiy (longiyart@gmail.com)
License: GPL-3.0-or-later
Copyright: 2025 longiy
Category: Paint
Location: Sidebar → Coloraide tab (default, customizable in preferences)
