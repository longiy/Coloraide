"""
Property definitions for color dynamics functionality.
"""

import bpy
from bpy.props import IntProperty, BoolProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating

class ColoraideDynamicsProperties(PropertyGroup):
    """Properties for color dynamics"""
    
    def update_strength(self, context):
        """Update handler for when dynamics strength changes"""
        if is_updating('dynamics'):
            return
            
        if self.strength > 0:
            # Start dynamics when strength is increased
            if not any(op.bl_idname == "brush.color_dynamics" 
                      for op in context.window_manager.operators):
                bpy.ops.brush.color_dynamics('INVOKE_DEFAULT')
        else:
            # Turn off dynamics when strength is zero
            self.running = False
    
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
        update=update_strength
    )
    
    def get_base_color(self, context):
        """Get the current base color for dynamics"""
        return tuple(context.window_manager.coloraide_picker.mean)