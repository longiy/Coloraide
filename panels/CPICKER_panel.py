"""
Core color picker panel UI implementation for Coloraide.
"""

import bpy

def draw_picker_panel(layout, context):
    wm = context.window_manager
    
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_picker", 
        text="Color Picker", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_picker else 'TRIA_RIGHT',
        emboss=False
    )
    
    if wm.coloraide_display.show_picker:
        # Create a single aligned column for all controls
        col = box.column(align=True)

        # Main color display row
        row = col.row(align=True)
        row.scale_y = 1
        split = row.split(factor=0.5, align=True)
        split.prop(wm.coloraide_picker, 'mean', text='')  # Area average (50%)
        split2 = split.split(factor=0.5, align=True)
        split2.prop(wm.coloraide_picker, 'current', text='')  # Current pixel (25%)
        split2.operator('image.screen_picker', text='', icon='EYEDROPPER').sqrt_length = 1  # Picker (25%)

        # Quick pick size control
        row = col.row(align=True)
        split = row.split(factor=0.75, align=True)
        split.prop(wm.coloraide_picker, 'custom_size', 
            text='Sample px', 
            slider=True,
        )
        split.operator('image.screen_picker', 
            text="", 
            icon='EYEDROPPER'
        ).sqrt_length = wm.coloraide_picker.custom_size

        # Normal picker
        row = col.row(align=True)
        row.operator("normal.color_picker", 
            text="Object Normal Picker",
            icon='NORMALS_VERTEX' if wm.coloraide_normal.enabled else 'NORMALS_VERTEX_FACE',
            depress=wm.coloraide_normal.enabled
        )
        
        # # Statistics (collapsible)
        # stats_box = box.box()
        # row = stats_box.row()
        # row.prop(wm.coloraide_display, "show_stats",
        #     text="Color Statistics",
        #     icon='TRIA_DOWN' if wm.coloraide_display.show_stats else 'TRIA_RIGHT',
        #     emboss=False
        # )
        
        # if wm.coloraide_display.show_stats:
        #     col = stats_box.column(align=True)
        #     col.prop(wm.coloraide_picker, 'max', text='Maximum')
        #     col.prop(wm.coloraide_picker, 'min', text='Minimum')
        #     col.prop(wm.coloraide_picker, 'median', text='Median')
        
    
        
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