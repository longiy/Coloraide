# 🎨 Coloraide Add-on - Version 1.4.8
Advanced color picker and manager for Blender 4.3+
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/Coloraide_Preview.png)
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/Coloraide_Preview2.png)

A comprehensive color management and selection tool for Blender.

## 🌟 Key Features

### 🔍 Quick Pick (**Shift+E**)
* **Real-time screen color sampling** activated by holding **Shift+E**.
* Customizable sample area (1-100 pixels) displays both **area average** and **single-pixel color** with a visual preview.

### 🎯 Normal Sampling
* Converts **3D mesh surface normals into RGB colors** for normal map workflows.
* Supports both **smooth and flat shading**.
* Includes **world-space normal sampling** in Texture Paint and Vertex Paint modes.

### 🎡 Color Wheel
* Visual **hue/saturation selector** with an integrated value slider.
* **Scalable size** (1.0-3.0x multiplier) for precision work.
* Includes a **hex input field** and a reset-to-default button.

### 🌈 Color Spaces
* **Multiple color representations** updated in real-time:
    * **RGB** (0-255 bytes)
    * **HSV** (360° hue, 0-100% sat/val)
    * **LAB** (perceptually uniform)
    * **Hex** (#RRGGBB)
* Conversions maintain **Photoshop-level accuracy** using scene linear color space internally.

### 📋 History & 🎨 Palettes
* **History:** Automatically stores recently used colors in an adjustable grid (**8-80 slots**). Click any swatch to instantly reapply. Features automatic duplicate prevention and a clear-all option.
* **Palettes:** Seamless integration with Blender's native palette system. Manage persistent color collections that save with your `.blend` files.

### 🖌️ Color Dynamics
* Native brush **color jitter control** (Blender 5.0+) for hue, saturation, and value randomization.
* Includes **per-stroke variation**, pressure sensitivity, and customizable pressure curves for natural painting.

---

## 🔧 Compatibility & Requirements

| Detail | Specification |
| :--- | :--- |
| **Version 1.4.8 Requirement** | Blender **4.5 or newer** for full feature support |
| **Version 1.4.7 Compatibility** | Blender 4.5 and earlier versions |
| **Supported Editors** | Image Editor, **3D View**, Clip Editor |
| **Supported Paint Modes** | Texture Paint, **Vertex Paint**, Weight Paint, Sculpt, Grease Pencil Draw, and Vertex Grease Pencil |

---

## ⌨️ Controls & Settings

### Keyboard Shortcut
* **Quick Pick:** **Shift+E** - Press and hold to sample, release to confirm.

### Panel Controls
* **Color Spaces:** Toggle **RGB/HSV/LAB** buttons in the Color Sliders section to show/hide.
* **History Size:** Use **+/- buttons** to adjust between 8-80 color slots.
* **Wheel Scale:** Drag slider (1.0-3.0x) or click the **reset button (↻)** to restore default (1.5x).
* **Panel Location:** Customizable in `Preferences` → `Add-ons` → `Coloraide` → `Tab Category`.

---

## 📦 Info

| Detail | Value |
| :--- | :--- |
| **Version** | 1.4.8 |
| **Author** | longiy (longiyart@gmail.com) |
| **License** | GPL-3.0-or-later |
| **Copyright** | 2025 longiy |
| **Category** | Paint |
| **Default Location** | Sidebar → **Coloraide tab** (customizable) |

***

Do you want to know more about the **Quick Pick (Shift+E)** feature or the **Color Dynamics**?
