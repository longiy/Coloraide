# Coloraide  - Color Picker Addon for Blender

A Blender addon for advanced color picking and management.

![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/ColorDynamics.gif?raw=true)
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/Coloraide_v1.1.1_Update_Colorwheel.gif?raw=true)
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/Coloraide_ColorHistory.gif?raw=true)
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/ColorPickerProPlus_gif.gif)
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/ColorPickerProPanel.png)

## Features

### Color Picking
- Quick Pick (Backslash \ shortcut)
- Press and hold to sample colors
- Shows current pixel color and area average
- Real-time color preview
- Adjustable sampling area
- Screen Picker
- Flexible sampling area (1x1 to custom size)
- Color statistics (mean, median, min/max)
- Live preview
- Multiple preset sizes (1x1, 5x5, custom)

### Color Management
- Interactive color wheel with adjustable size
- Multiple color space support:
- RGB (0-255) values with channel control
- LAB color space
- Hex color input/output
- Color Dynamics
- Random color variation during brush strokes
- Adjustable strength (0-100%)
- Real-time color randomization

### Color History
- Color storage system
- Adjustable history size (8-80 slots)
- Duplicate prevention
- Grid-based display
- Quick color reuse
- Visual history management
- Expandable/collapsible interface
- Size adjustment controls
- Grid layout

### Tool Integration
Works with:
- Grease Pencil brushes
- Texture Paint brushes
- Unified color settings
- Brush color dynamics

### Editor Support
Available in:
- Image Editor
- 3D Viewport
- Clip Editor

## Usage

### Quick Pick Mode
1. Press and hold Backslash (\\)
2. Move cursor over desired colors
3. View real-time preview
4. Release to confirm selection

### Screen Picker
1. Adjust sampling size using the slider
2. Click the eyedropper icon
3. Choose size or use custom area
4. Select color

### Color Dynamics
1. Enable by adjusting strength slider
2. Paint to see color variations
3. Adjust strength as needed
4. Colors reset after stroke

### Color History
- Colors save automatically when picked
- Click saved colors to reuse
- Adjust history size with +/- buttons
- Toggle history visibility

### Color Spaces
- RGB: Direct 0-255 value input per channel
- LAB: 
  - L: Lightness (0-100)
  - a: Green-Red (-128 to +127)
  - b: Blue-Yellow (-128 to +127)
- Hex: Standard 6-digit hex color codes (#RRGGBB)

## Requirements
- Blender 4.2.0 or later
- OpenGL-compatible graphics card

## Credits
Created by longiy  
Licensed under GNU General Public License v3.0

