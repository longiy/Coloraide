# Coloraide

A Blender addon for advanced color picking and management.
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/Coloraide_ColorHistory.gif?raw=true)
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/ColorPickerProPlus_gif.gif)
![Image Description](https://github.com/longiy/static-assets/blob/main/coloraide-assets/ColorPickerProPanel.png)

## Overview

Coloraide is a versatile color picker addon for Blender that enhances the default color picking functionality with features like:
- Multi-pixel sampling
- Color history management
- Real-time color statistics
- Multiple sampling methods
- Integration with Grease Pencil and Texture Paint tools

## Installation

1. Download the Coloraide addon
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install" and select the downloaded file
4. Enable the addon by checking its checkbox

## Features

### Color Sampling Methods

#### Quick Pick
- Press and hold to activate color picker
- Release to select color
- Updates brush colors in real-time
- Shows both current pixel color and mean color of sampling area

#### Screen Picker
- Click to sample colors
- Adjustable sampling area (1x1 to custom size)
- Provides real-time color statistics:
  - Mean color
  - Median color
  - Maximum brightness color
  - Minimum brightness color
- Automatically updates active brush colors

#### Rectangle Selection
- Click and drag to define a rectangular area
- Right-click to complete selection
- Calculates color statistics for the entire selected area
- Ideal for sampling larger areas or getting color averages

### Color History

- Maintains a history of recently picked colors
- Configurable history size (5-30 colors)
- Prevents duplicate colors
- Click any color in history to reuse it
- Colors are displayed in rows of 5 for easy access

### Interface

The addon adds panels in three locations:
- Image Editor > Sidebar > Color tab
- 3D Viewport > Sidebar > Color tab
- Clip Editor > Sidebar > Color tab

Each panel includes:
- Current and mean color displays
- Color history with size controls
- Min/Max color values
- Sampling size controls
- Quick access buttons for common sampling sizes (1x1, 5x5)
- Custom sampling size slider
- Rectangle selection tool

### Tool Integration

Automatically updates colors for:
- Grease Pencil brushes
- Texture Paint brushes
- Unified color settings (when enabled)

## Usage Tips

1. **Quick Sampling**: Use the 1x1 picker for precise color selection from single pixels.
2. **Area Sampling**: Use 5x5 or custom size for averaging colors in an area.
3. **Large Area Analysis**: Use the rectangle tool to analyze colors in larger regions.
4. **Color History**: 
   - Use +/- buttons to adjust history size
   - Click any color in history to reuse it
   - History automatically prevents duplicates

## Technical Details

### Sampling Methods

- Single pixel: Direct color sampling
- Area sampling: Calculates various statistics:
  - Mean color value
  - Median color value
  - Maximum brightness color
  - Minimum brightness color
- Rectangle: User-defined area sampling with comprehensive color analysis

### Color Processing

- Uses NumPy for efficient color calculations
- Handles RGB color values in floating-point format (0.0-1.0)
- Supports alpha channel (though primarily works with RGB)

### GPU Integration

- Uses Blender's GPU module for efficient screen sampling
- Supports both older and newer Blender versions (adapts shader types based on version)
- Real-time preview of sampling area and selected colors

## Requirements

- Blender 2.8x or later
- GPU with OpenGL support

## License

This program is licensed under the GNU General Public License v3.0 or later.

## Credits

Originally created by Spencer Magnusson (semagnum@gmail.com)  
Modified by longiy (longiyart@gmail.com)

## Troubleshooting

If you encounter issues:

1. **Shader Initialization Fails**:
   - Check GPU driver updates
   - Verify Blender's OpenGL support
   - Try restarting Blender

2. **Color Updates Not Working**:
   - Verify tool settings are accessible
   - Check if unified color settings are enabled
   - Ensure proper brush selection

3. **Performance Issues**:
   - Reduce sampling area size
   - Avoid sampling extremely large rectangular areas
   - Check system GPU performance

