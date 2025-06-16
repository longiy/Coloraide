# COLORAIDE_dynamics_properties.py
import bpy
from bpy.props import IntProperty, BoolProperty, FloatVectorProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import is_updating

class ColoraideDynamicsProperties(PropertyGroup):
    """Color dynamics control properties"""
    
    def update_dynamics(self, context):
        """Trigger color dynamics operator when strength changes"""
        if is_updating():
            return
        
        if self.strength > 0:
            # Store current color as master color when enabling dynamics
            if hasattr(context.window_manager, 'coloraide_picker'):
                current_color = tuple(context.window_manager.coloraide_picker.mean)
                self.master_color = current_color
            
            # Automatically start color dynamics if not already running
            if not any(op.bl_idname == "color.color_dynamics" for op in context.window_manager.operators):
                bpy.ops.color.color_dynamics('INVOKE_DEFAULT')
        else:
            # Stop color dynamics when strength is zero
            self.running = False

    running: BoolProperty(
        name="Color Dynamics Active",
        default=False
    )
    
    strength: IntProperty(
        name="Color Dynamics",
        description="Amount of random color variation during strokes",
        min=0,
        max=100,
        default=0,
        subtype='PERCENTAGE',
        update=update_dynamics
    )
    
    show_color_sliders: BoolProperty(
        name="Show Color Sliders",
        description="Show color space sliders",
        default=True
    )
    
    show_dynamics: BoolProperty(
        name="Show Color Dynamics",
        description="Show color dynamics controls",
        default=True
    )

    # NEW: Store the master color for dynamics
    master_color: FloatVectorProperty(
        name="Master Color",
        description="Base color for dynamics randomization",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0)
    )
    

def register():
    # No special registration needed beyond standard Blender property group registration
    pass

def unregister():
    # No special unregistration needed
    pass