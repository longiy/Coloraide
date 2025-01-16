"""
BRUSH_OT_normal_color_picker.py
Operator for sampling object or tangent space normals as colors for painting
"""

import bpy
import gpu
import numpy as np
from mathutils import Vector, Matrix
from bpy.props import BoolProperty, EnumProperty, FloatVectorProperty
from bpy_extras import view3d_utils

def normal_to_color(normal):
    """Convert a normal vector to RGB color values"""
    # Remap from [-1,1] to [0,1] range
    return tuple((n + 1.0) * 0.5 for n in normal)

def get_tangent_space_normal(obj, loop_index, normal):
    """Convert object space normal to tangent space using active UV map"""
    mesh = obj.data
    
    # Ensure we have UV data
    if not mesh.uv_layers.active:
        return normal
    
    # Get the tangent matrix for this loop
    if not mesh.loops[loop_index].tangent:
        mesh.calc_tangents()
        
    # Get tangent space vectors
    loop = mesh.loops[loop_index]
    tangent = Vector(loop.tangent)
    bitangent = Vector(loop.bitangent)
    normal_vec = Vector(normal)
    
    # Create tangent space matrix
    tangent_matrix = Matrix([
        tangent,
        bitangent,
        normal_vec
    ]).transposed()
    
    # Transform normal to tangent space
    tangent_normal = tangent_matrix @ normal_vec
    return tangent_normal

class BRUSH_OT_normal_color_picker(bpy.types.Operator):
    bl_idname = "brush.normal_color_picker"
    bl_label = "Use Normal as Color"
    bl_description = "Sample normals as colors when painting"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if not context.active_object or not context.active_object.type == 'MESH':
            return False
        if context.mode not in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_WEIGHT'}:
            return False
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        # Toggle the enabled state
        wm.normal_picker.enabled = not wm.normal_picker.enabled
        
        if wm.normal_picker.enabled:
            context.window_manager.modal_handler_add(self)
            context.window.cursor_modal_set('EYEDROPPER')
            return {'RUNNING_MODAL'}
            
        context.window.cursor_modal_restore()
        return {'FINISHED'}

    def get_surface_normal(self, context, obj, hit_location, normal, loop_index):
        """Get normal in the requested space"""
        if context.window_manager.normal_picker.space == 'TANGENT':
            # Check if object has UV maps
            if not obj.data.uv_layers:
                self.report({'WARNING'}, "Object needs UV map for tangent space normals")
                return normal
            return get_tangent_space_normal(obj, loop_index, normal)
        else:  # 'OBJECT'
            return normal

    def sample_normal_at_mouse(self, context, event):
        """Sample normal at current mouse position"""
        # Get the active object
        obj = context.active_object
        if not obj or not obj.data or obj.type != 'MESH':
            return None
            
        # Verify we're in a 3D view
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return None
            
        # Get view ray
        coord = event.mouse_region_x, event.mouse_region_y
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        
        # Transform ray to local space
        matrix = obj.matrix_world
        matrix_inv = matrix.inverted()
        ray_target = ray_origin + view_vector * 1000.0
        
        local_ray_origin = matrix_inv @ ray_origin
        local_ray_target = matrix_inv @ ray_target
        local_ray_direction = (local_ray_target - local_ray_origin).normalized()

        # Perform raycast
        success, location, normal, face_index = obj.ray_cast(local_ray_origin, local_ray_direction)
        
        if success:
            # Get loop index for tangent space calculation if needed
            loop_index = -1
            if context.window_manager.normal_picker.space == 'TANGENT':
                # Find the closest loop to hit point
                mesh = obj.data
                if mesh.polygons and face_index >= 0:
                    poly = mesh.polygons[face_index]
                    loop_index = poly.loop_start
            
            # Get normal in requested space
            final_normal = self.get_surface_normal(context, obj, location, normal, loop_index)
            
            # Convert to color
            return normal_to_color(final_normal)
            
        return None

    def update_colors(self, context, color):
        """Update all color properties with the given color"""
        if not color:
            return
            
        # Update brush color
        ts = context.tool_settings
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = color
        
        # Update color picker display
        wm = context.window_manager
        wm.coloraide_picker.mean = color
        wm.coloraide_picker.current = color
        wm.coloraide_wheel.color = (*color, 1.0)

    def modal(self, context, event):
        if not context.window_manager.normal_picker.enabled:
            if context.window:
                context.window.cursor_modal_restore()
            return {'CANCELLED'}

        # Check if we're in a valid 3D View area
        area = context.area
        if not area or area.type != 'VIEW_3D':
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            # Ensure mouse is within the area
            if (0 <= event.mouse_x - area.x <= area.width and 
                0 <= event.mouse_y - area.y <= area.height):
                # Sample and update color on mouse movement
                color = self.sample_normal_at_mouse(context, event)
                if color:
                    self.update_colors(context, color)
                area.tag_redraw()

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                # When painting starts, use current sampled color
                color = self.sample_normal_at_mouse(context, event)
                if color:
                    self.update_colors(context, color)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window.cursor_modal_restore()
            context.window_manager.normal_picker.enabled = False
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BRUSH_OT_normal_color_picker)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_normal_color_picker)