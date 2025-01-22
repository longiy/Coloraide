"""
Core color picker panel UI implementation for Coloraide.
"""

import bpy

def draw_picker_panel(layout, context):
    """Draw core color picker controls in the given layout"""
    wm = context.window_manager
    
    # Core color picker box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_picker", 
        text="Color Picker", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_picker else 'TRIA_RIGHT',
        emboss=False
    )
    
    if wm.coloraide_display.show_picker:
        # Main color display row
        row = box.row(align=True)
        row.scale_y = 2.0
        row.prop(wm.coloraide_picker, 'mean', text='')  # Area average
        row.prop(wm.coloraide_picker, 'current', text='')  # Current pixel
        
        # Statistics (collapsible)
        stats_box = box.box()
        row = stats_box.row()
        row.prop(wm.coloraide_display, "show_stats",
            text="Color Statistics",
            icon='TRIA_DOWN' if wm.coloraide_display.show_stats else 'TRIA_RIGHT',
            emboss=False
        )
        
        if wm.coloraide_display.show_stats:
            col = stats_box.column(align=True)
            col.prop(wm.coloraide_picker, 'max', text='Maximum')
            col.prop(wm.coloraide_picker, 'min', text='Minimum')
            col.prop(wm.coloraide_picker, 'median', text='Median')
        
        # Quick pick size control
        row = box.row(align=True)
        row.prop(wm.coloraide_picker, 'custom_size', text="Sample Size", slider=True)
        
        # Quick pick operators
        row = box.row(align=True)
        row.operator('image.screen_picker', 
            text=f"{wm.coloraide_picker.custom_size}x{wm.coloraide_picker.custom_size} Sample", 
            icon='EYEDROPPER'
        ).sqrt_length = wm.coloraide_picker.custom_size
        
        # Common sample sizes
        row = box.row(align=True)
        row.operator('image.screen_picker', text='1x1', icon='EYEDROPPER').sqrt_length = 1
        row.operator('image.screen_picker', text='5x5', icon='EYEDROPPER').sqrt_length = 5
        row.operator('image.screen_picker', text='10x10', icon='EYEDROPPER').sqrt_length = 10

class PICKER_PT_panel:
    """Class containing panel drawing methods for core color picker"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the color picker"""
        wm = context.window_manager
        if wm.coloraide_display.show_picker:
            row = layout.row(align=True)
            row.prop(wm.coloraide_picker, 'mean', text='')
            row.prop(wm.coloraide_picker, 'current', text='')
            row.operator('image.screen_picker', text='', icon='EYEDROPPER').sqrt_length = wm.coloraide_picker.custom_size
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full color picker panel"""
        draw_picker_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal color picker controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_picker:
            row = layout.row(align=True)
            row.prop(wm.coloraide_picker, 'mean', text='')
            row.prop(wm.coloraide_picker, 'custom_size', text='')

def register():
    """Register any classes specific to the picker panel"""
    pass

def unregister():
    """Unregister any classes specific to the picker panel"""
    pass