"""
Normal sampling panel UI implementation for Coloraide.
"""

import bpy

def draw_normal_panel(layout, context):
    """Draw normal sampling controls in the given layout"""
    wm = context.window_manager
    
    # Normal sampler box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_normal_sampler", 
        text="Normal Color Sampler", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_normal_sampler else 'TRIA_RIGHT',
        emboss=False
    )
    
    if wm.coloraide_display.show_normal_sampler:
        # Enable button
        row = box.row()
        row.operator(
            "brush.sample_normal",
            text="Sample Normals",
            icon='NORMALS_VERTEX' if wm.coloraide_normal.enabled else 'NORMALS_VERTEX_FACE',
            depress=wm.coloraide_normal.enabled
        )
        
        # Space selection when enabled
        if wm.coloraide_normal.enabled:
            row = box.row()
            row.prop(wm.coloraide_normal, "space")
            
            # Help text
            if wm.coloraide_normal.space == 'TANGENT':
                box.label(text="Note: Requires UV map", icon='INFO')

class NORMAL_PT_panel:
    """Class containing panel drawing methods for normal sampling"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the normal sampling controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_normal_sampler:
            row = layout.row(align=True)
            row.operator(
                "brush.sample_normal",
                text="Sample Normals",
                icon='NORMALS_VERTEX' if wm.coloraide_normal.enabled else 'NORMALS_VERTEX_FACE',
                depress=wm.coloraide_normal.enabled
            )
            if wm.coloraide_normal.enabled:
                row.prop(wm.coloraide_normal, "space", text="")
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full normal sampling panel"""
        draw_normal_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal normal sampling controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_normal_sampler and wm.coloraide_normal.enabled:
            layout.prop(wm.coloraide_normal, "space", text="")

def register():
    """Register any classes specific to the normal panel"""
    pass

def unregister():
    """Unregister any classes specific to the normal panel"""
    pass