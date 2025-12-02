"""
Core color picker panel UI implementation for Coloraide.
CLEANED: Removed unused class methods (draw_compact, draw_expanded, draw_minimal).
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
        split.operator('image.screen_picker_quick', 
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


def register():
    """Register any classes specific to the picker panel"""
    pass


def unregister():
    """Unregister any classes specific to the picker panel"""
    pass