"""Normal color sampling operator with simplified functionality."""
import bpy
import gpu
import numpy as np
from mathutils import Vector
from bpy.props import BoolProperty
from bpy.types import Operator
from bpy_extras import view3d_utils
from ..COLORAIDE_sync import sync_all

def normal_to_color(normal):
    """Convert normal vector to RGB color values"""
    return tuple((n + 1.0) * 0.5 for n in normal)

class NORMAL_OT_color_picker(Operator):
    bl_idname = "normal.color_picker"
    bl_label = "Normal Color Picker"
    bl_description = "Sample object space normals as colors for painting"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if context.area.type != 'VIEW_3D':
            return False
        if not context.active_object or not context.active_object.type == 'MESH':
            return False
        # Allow in texture paint mode
        if context.mode not in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_WEIGHT'}:
            return False
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        wm.coloraide_normal.enabled = not wm.coloraide_normal.enabled
        
        if wm.coloraide_normal.enabled:
            context.window_manager.modal_handler_add(self)
            context.window.cursor_modal_set('EYEDROPPER')
            return {'RUNNING_MODAL'}
            
        context.window.cursor_modal_restore()
        return {'FINISHED'}

    def sample_normal_from_3d_view(self, context, event):
        """Sample normal using 3D view raycast with proper loop normal support"""
        obj = context.active_object
        if not obj or not obj.data or obj.type != 'MESH':
            return None
            
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return None
            
        coord = event.mouse_region_x, event.mouse_region_y
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        
        # Get evaluated version with all modifiers applied
        depsgraph = context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        eval_mesh = eval_obj.data
        
        matrix = eval_obj.matrix_world
        matrix_inv = matrix.inverted()
        ray_target = ray_origin + view_vector * 1000.0
        
        local_ray_origin = matrix_inv @ ray_origin
        local_ray_target = matrix_inv @ ray_target
        local_ray_direction = (local_ray_target - local_ray_origin).normalized()

        # Perform raycast
        success, location, normal, face_index = eval_obj.ray_cast(local_ray_origin, local_ray_direction)
        
        if not success:
            return None

        face = eval_mesh.polygons[face_index]
        
        if face.use_smooth:
            # For smooth shading, use loop normals
            vertices = []
            loop_normals = []
            
            # Get vertices and loop normals for the face
            for loop_idx in range(face.loop_start, face.loop_start + face.loop_total):
                loop = eval_mesh.loops[loop_idx]
                vertices.append(eval_mesh.vertices[loop.vertex_index].co)
                loop_normals.append(loop.normal)

            # Calculate barycentric coordinates for interpolation
            def get_barycentric_weights(p, a, b, c):
                v0 = b - a
                v1 = c - a
                v2 = p - a
                
                d00 = v0.dot(v0)
                d01 = v0.dot(v1)
                d11 = v1.dot(v1)
                d20 = v2.dot(v0)
                d21 = v2.dot(v1)
                
                denom = d00 * d11 - d01 * d01
                if abs(denom) < 1e-6:
                    return (1.0/3.0, 1.0/3.0, 1.0/3.0)
                    
                v = (d11 * d20 - d01 * d21) / denom
                w = (d00 * d21 - d01 * d20) / denom
                u = 1.0 - v - w
                
                return (u, v, w)

            # Use first 3 vertices for barycentric coordinates
            weights = get_barycentric_weights(location, vertices[0], vertices[1], vertices[2])
            
            # Interpolate normal using barycentric coordinates
            normal = Vector((0, 0, 0))
            for w, n in zip(weights, loop_normals[:3]):
                normal += w * n
            normal.normalize()
        
        # Transform normal to world space
        world_normal = (matrix.inverted().transposed().to_3x3() @ normal).normalized()
        
        return normal_to_color(world_normal)

    def modal(self, context, event):
        if not context.window_manager.coloraide_normal.enabled:
            context.window.cursor_modal_restore()
            return {'CANCELLED'}

        area = context.area
        if not area or area.type != 'VIEW_3D':
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            if (0 <= event.mouse_x - area.x <= area.width and 
                0 <= event.mouse_y - area.y <= area.height):
                color = self.sample_normal_from_3d_view(context, event)
                if color:
                    sync_all(context, 'picker', color)
                    area.tag_redraw()

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                color = self.sample_normal_from_3d_view(context, event)
                if color:
                    sync_all(context, 'picker', color)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window.cursor_modal_restore()
            context.window_manager.coloraide_normal.enabled = False
            return {'CANCELLED'}

        return {'PASS_THROUGH'}