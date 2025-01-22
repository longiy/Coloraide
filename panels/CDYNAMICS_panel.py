"""
Color dynamics panel UI implementation for Coloraide.
"""

import bpy

def draw_dynamics_panel(layout, context):
    """Draw color dynamics controls in the given layout"""
    wm = context.window_manager
    
    # Dynamics box with toggle
    box = layout.box()
    row = box.row()
    row.prop(wm.coloraide_display, "show_dynamics", 
        text="Color Dynamics", 
        icon='TRIA_DOWN' if wm.coloraide_display.show_dynamics else 'TRIA_RIGHT',
        emboss=False
    )
    
    if wm.coloraide_display.show_dynamics:
        # Strength slider
        row = box.row(align=True)
        row.prop(wm.coloraide_dynamics, "strength", text="Strength", slider=True)
        
        # Reset button
        row.operator(
            "brush.reset_dynamics",
            text="",
            icon='LOOP_BACK'
        )
        
        # Status and help text
        if wm.coloraide_dynamics.running:
            box.label(text="Active - Click and drag to paint", icon='INFO')
        elif wm.coloraide_dynamics.strength > 0:
            box.label(text="Ready - Start painting to activate", icon='INFO')

class BRUSH_OT_reset_dynamics(bpy.types.Operator):
    """Reset color dynamics settings"""
    bl_idname = "brush.reset_dynamics"
    bl_label = "Reset Dynamics"
    bl_description = "Reset color dynamics settings to default"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        dynamics = context.window_manager.coloraide_dynamics
        dynamics.strength = 0
        dynamics.running = False
        return {'FINISHED'}

class DYNAMICS_PT_panel:
    """Class containing panel drawing methods for color dynamics"""
    
    @staticmethod
    def draw_compact(layout, context):
        """Draw a compact version of the dynamics controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_dynamics:
            row = layout.row(align=True)
            row.prop(wm.coloraide_dynamics, "strength", text="Dynamics")
    
    @staticmethod
    def draw_expanded(layout, context):
        """Draw the full dynamics panel"""
        draw_dynamics_panel(layout, context)
    
    @staticmethod
    def draw_minimal(layout, context):
        """Draw minimal dynamics controls"""
        wm = context.window_manager
        if wm.coloraide_display.show_dynamics:
            layout.prop(wm.coloraide_dynamics, "strength", text="")

def register():
    bpy.utils.register_class(BRUSH_OT_reset_dynamics)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_reset_dynamics)