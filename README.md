# 🎨 Coloraide Add-on - Version 1.5.0
Advanced color picker and manager for Blender 4.5+
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

### 🎨 Object Colors (**NEW in 1.5.0**)
* **Auto-detects colors** from selected objects across materials, lights, Geometry Nodes, Grease Pencil, and object properties.
* **Two display modes:**
    * **Object Mode:** View individual properties organized by object.
    * **Grouped Mode:** Figma-style grouping of identical colors with usage counts.
* **Live Sync:** Toggle to update object colors in real-time as you adjust Coloraide.
* **Push/Pull workflow:** Load colors from objects (↑) or apply colors to objects (↓).
* **Performance optimized:** Handles 200+ properties with three update modes (Immediate, Batched, On Release).

---

## 🔧 Compatibility & Requirements

| | |
| :--- | :--- |
| **Version 1.5.0 Requirement** | Blender **4.5 or newer** for full feature support |
| **Supported Editors** | Image Editor, 3D View, Clip Editor |
| **Supported Paint Modes** | Texture Paint, Vertex Paint, Weight Paint, Sculpt, Grease Pencil Draw, and Vertex Grease Pencil |

---

## ⌨️ Controls & Settings

### Keyboard Shortcut
* **Quick Pick:** **Shift+E** - Press and hold to sample, release to confirm.

### Panel Controls
* **Color Spaces:** Toggle **RGB/HSV/LAB** buttons in the Color Sliders section to show/hide.
* **History Size:** Use **+/- buttons** to adjust between 8-80 color slots.
* **Wheel Scale:** Drag slider (1.0-3.0x) or click the **reset button (↻)** to restore default (1.5x).
* **Object Colors:** "Multi" toggle to scan all selected objects or active only. Switch between Object/Grouped modes.
* **Panel Visibility:** Customize in `Preferences` → `Add-ons` → `Coloraide` → enable/disable individual panels.
* **Panel Location:** Customizable in `Preferences` → `Add-ons` → `Coloraide` → `Tab Category`.

### Performance Settings
* **Live Sync Update Mode** (in Preferences):
    * **Immediate:** Updates instantly - best for <50 properties.
    * **Batched (100ms):** Smooth with minimal delay - recommended.
    * **On Mouse Release:** Fastest for heavy scenes (200+ properties).

---

## 🎓 Use Cases

* **Material Library Management:** Sync colors across multiple materials instantly.
* **Lighting Setups:** Coordinate light colors for consistent mood.
* **Color Theming:** Apply palette changes across entire scenes.
* **GeoNodes Workflows:** Manage color parameters in procedural setups.
* **Grease Pencil:** Coordinate fill/stroke colors across materials.

---

## 📦 Info

| | |
| :--- | :--- |
| **Version** | 1.5.0 |
| **Author** | longiy (longiyart@gmail.com) |
| **License** | GPL-3.0-or-later |
| **Copyright** | 2025 longiy |
| **Category** | Paint |
| **Default Location** | Sidebar → **Coloraide tab** (customizable) |

---

## 🚀 What's New in 1.5.0

* **Object Colors Panel** with auto-detection and live sync
* **Grouped Mode** for Figma-style color management
* **90% performance improvement** for live-synced properties
* **Python caching system** for smooth slider adjustments
* **Instant object scan refresh** with smart caching
* **Collapsible panels** for cleaner workspace
* **Panel visibility controls** in addon preferences
* **Enhanced error handling** with better stability

---

***

Want to know more about the **Object Colors** panel or **Live Sync** features?
