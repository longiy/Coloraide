"""
Color wheel panel UI implementation for Coloraide.
"""

import bpy

def draw_wheel_panel(layout, context):
    """Draw color wheel controls in the given layout"""
    wm = context.window_manager
    
    # Color wheel box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_wheel", 
        text="Color Wheel", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_wheel else 'TRIA_RIGHT', 
        emboss=False
    )
    
    if wm.coloraide_display.show_wheel:
        # Scale the color wheel based on user preference
        col = box.column()
        col.scale_y = wm.coloraide_wheel.scale
        
        # Add the main color wheel
        col.template_color_picker(
            wm.coloraide_wheel, 
            "color", 
            value_slider=True,
            lock_luminosity=False
        )
        
        # Add scale control and reset button
        row = box.row(align=True)
        split = row.split(factor=0.85, align=True)
        split.prop(wm.coloraide_wheel, "scale", text="Size", slider=True)
        split.operator(
            "color.reset_wheel_scale",
            text="",
            icon='LOOP_BACK'
        )

class WHEEL_PT_panel:
    """Class containing panel drawing methods for color wheel"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the color wheel"""
        wm = context.window_manager
        if wm.coloraide_display.show_wheel:
            col = layout.column()
            col.scale_y = wm.coloraide_wheel.scale
            col.template_color_picker(
                wm.coloraide_wheel,
                "color",
                value_slider=True,
                lock_luminosity=False
            )
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full color wheel panel"""
        draw_wheel_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal color wheel without controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_wheel:
            layout.template_color_picker(
                wm.coloraide_wheel,
                "color",
                value_slider=False,
                lock_luminosity=False
            )

def register():
    """Register any classes specific to the wheel panel"""
    pass

def unregister():
    """Unregister any classes specific to the wheel panel"""
    pass