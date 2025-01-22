"""
Property definitions for color dynamics functionality.
"""

import bpy
from bpy.props import IntProperty, BoolProperty
from bpy.types import PropertyGroup

def update_color_dynamics(self, context):
    """Update handler for when dynamics strength changes"""
    if self.strength > 0:
        # Check if dynamics operator is already running
        if not any(op.bl_idname == "brush.color_dynamics" 
                  for op in context.window_manager.operators):
            bpy.ops.brush.color_dynamics('INVOKE_DEFAULT')
    else:
        # Turn off dynamics
        self.running = False

class ColoraideDynamicsProperties(PropertyGroup):
    """Properties for color dynamics"""
    
    running: BoolProperty(
        name="Color Dynamics Running",
        description="Whether color dynamics is currently active",
        default=False
    )
    
    strength: IntProperty(
        name="Strength",
        description="Amount of random color variation during strokes",
        min=0,
        max=100,
        default=0,
        subtype='PERCENTAGE',
        update=update_color_dynamics
    )
    
    def get_base_color(self, context):
        """Get the current base color for dynamics"""
        return tuple(context.window_manager.coloraide_picker.mean)

