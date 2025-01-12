# Coloraide - Color Picker Addon for Blender

## Overview
Coloraide extends Blender's color picking functionality with additional features and color space options.

## Features

### Color Picking
- Quick Pick (Backslash \ shortcut)
  - Press and hold to sample colors
  - Shows current pixel color and area average
  - Updates colors in real-time
- Screen Picker
  - Adjustable sampling area (1x1 to custom size)
  - Shows color statistics (mean, median, min/max)
  - Real-time preview

### Color Management
- Interactive color wheel with adjustable size
- Color spaces:
  - RGB (0-255) values
  - LAB color space
  - Hex color input/output
- Color history:
  - Stores recent colors
  - Configurable size (5-50 slots)
  - Prevents duplicates
  - Quick color reuse

### Tool Integration
Works with:
- Grease Pencil brushes
- Texture Paint brushes
- Unified color settings

### Editor Support
Available in:
- Image Editor
- 3D Viewport
- Clip Editor

## Installation
1. Download the addon
2. Go to Edit > Preferences > Add-ons
3. Click "Install" and select the file
4. Enable the addon

## Usage

### Quick Pick
1. Press and hold Backslash
2. Move cursor over desired color
3. Release to select

### Screen Picker
1. Choose sampling size
2. Click the eyedropper icon
3. Select color

### Color History
- Colors save automatically when picked
- Click saved colors to reuse them
- Adjust history size with +/- buttons

### Color Spaces
- RGB: Direct 0-255 value input
- LAB: 
  - L: Lightness (0-100)
  - a: Green-Red (-128 to +127)
  - b: Blue-Yellow (-128 to +127)
- Hex: Standard hex color codes

## Requirements
- Blender 3.2.0 or later
- OpenGL-capable GPU

## Credits
Created by Spencer Magnusson & longiy
GNU General Public License v3.0
