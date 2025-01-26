"""Normal color sampling operator with subdivision support."""
import bpy
import gpu
import numpy as np
from mathutils import Vector, Matrix
from bpy.props import BoolProperty
from bpy.types import Operator
from bpy_extras import view3d_utils
from ..COLORAIDE_sync import sync_all

def normal_to_color(normal):
    """Convert normal vector to RGB color values"""
    return tuple((n + 1.0) * 0.5 for n in normal)

def get_tangent_space_normal(obj, loop_index, normal):
    """Convert object space normal to tangent space"""
    mesh = obj.data
    if not mesh.uv_layers.active:
        return normal
    
    if not mesh.loops[loop_index].tangent:
        mesh.calc_tangents()
        
    loop = mesh.loops[loop_index]
    tangent = Vector(loop.tangent)
    bitangent = Vector(loop.bitangent)
    normal_vec = Vector(normal)
    
    tangent_matrix = Matrix([
        tangent,
        bitangent,
        normal_vec
    ]).transposed()
    
    return tangent_matrix @ normal_vec

def point_in_triangle(p, a, b, c, epsilon=1e-5):
    """Check if point p is inside triangle abc using area method"""
    def area(x1, y1, x2, y2, x3, y3):
        return abs((x1*(y2-y3) + x2*(y3-y1)+ x3*(y1-y2))/2.0)
    
    A = area(a.x, a.y, b.x, b.y, c.x, c.y)
    A1 = area(p.x, p.y, b.x, b.y, c.x, c.y)
    A2 = area(a.x, a.y, p.x, p.y, c.x, c.y)
    A3 = area(a.x, a.y, b.x, b.y, p.x, p.y)
    
    return abs(A - (A1 + A2 + A3)) < epsilon

def find_face_from_uv(obj, uv_coord, epsilon=1e-5):
    """Find face containing UV coordinate with subdivision support"""
    mesh = obj.data
    if not mesh.uv_layers.active:
        return None, None, None
    
    uv_layer = mesh.uv_layers.active
    
    # Try finding exact face first
    for poly in mesh.polygons:
        uvs = [Vector(uv_layer.data[loop_idx].uv) for loop_idx in poly.loop_indices]
        
        if len(uvs) == 3:
            if point_in_triangle(Vector(uv_coord), uvs[0], uvs[1], uvs[2], epsilon):
                return poly, None, poly.loop_indices[0]
        elif len(uvs) == 4:
            # Split quad into two triangles
            if (point_in_triangle(Vector(uv_coord), uvs[0], uvs[1], uvs[2], epsilon) or
                point_in_triangle(Vector(uv_coord), uvs[2], uvs[3], uvs[0], epsilon)):
                return poly, None, poly.loop_indices[0]
    
    # If exact match fails, find closest face
    min_dist = float('inf')
    closest_face = None
    closest_loop = None
    
    for poly in mesh.polygons:
        uvs = [Vector(uv_layer.data[loop_idx].uv) for loop_idx in poly.loop_indices]
        center = sum(uvs, Vector((0,0))) / len(uvs)
        dist = (Vector(uv_coord) - center).length
        
        if dist < min_dist:
            min_dist = dist
            closest_face = poly
            closest_loop = poly.loop_indices[0]
    
    if closest_face and min_dist < 1.0:  # Threshold for maximum distance
        return closest_face, None, closest_loop
        
    return None, None, None

class NORMAL_OT_color_picker(Operator):
    bl_idname = "normal.color_picker"
    bl_label = "Normal Color Picker"
    bl_description = "Sample normals as colors for painting"
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
        wm.coloraide_normal.enabled = not wm.coloraide_normal.enabled
        
        if wm.coloraide_normal.enabled:
            context.window_manager.modal_handler_add(self)
            context.window.cursor_modal_set('EYEDROPPER')
            return {'RUNNING_MODAL'}
            
        context.window.cursor_modal_restore()
        return {'FINISHED'}

    def get_surface_normal(self, context, obj, hit_location, normal, loop_index):
        """Get normal in the requested space"""
        if context.window_manager.coloraide_normal.space == 'TANGENT':
            if not obj.data.uv_layers:
                self.report({'WARNING'}, "Object needs UV map for tangent space normals")
                return normal
            return get_tangent_space_normal(obj, loop_index, normal)
        return normal

    def create_eval_obj(self, context, obj):
        """Create evaluated version of object with modifiers"""
        depsgraph = context.evaluated_depsgraph_get()
        return obj.evaluated_get(depsgraph)

    def sample_normal_from_3d_view(self, context, event):
        """Sample normal using 3D view raycast with subdivision support"""
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
        
        # Get evaluated version of the object with modifiers applied
        eval_obj = self.create_eval_obj(context, obj)
        
        matrix = eval_obj.matrix_world
        matrix_inv = matrix.inverted()
        ray_target = ray_origin + view_vector * 1000.0
        
        local_ray_origin = matrix_inv @ ray_origin
        local_ray_target = matrix_inv @ ray_target
        local_ray_direction = (local_ray_target - local_ray_origin).normalized()

        success, location, normal, face_index = eval_obj.ray_cast(local_ray_origin, local_ray_direction)
        
        if success:
            # Use the evaluated mesh data
            eval_mesh = eval_obj.data
            if face_index >= len(eval_mesh.polygons):
                # If face index is out of range, just use the normal directly
                final_normal = normal
            else:
                loop_index = eval_mesh.polygons[face_index].loop_start
                final_normal = self.get_surface_normal(context, eval_obj, location, normal, loop_index)
                
            return normal_to_color(final_normal)
            
        return None

    def sample_normal_from_uv_editor(self, context, event):
        """Sample normal by mapping UV space to 3D geometry"""
        obj = context.active_object
        if not obj or not obj.data or obj.type != 'MESH':
            return None

        region = context.region
        if not region:
            return None

        # Convert mouse coordinates to UV space
        mouse_uv_x = (event.mouse_region_x - region.x) / region.width
        mouse_uv_y = (event.mouse_region_y - region.y) / region.height
        uv_coord = Vector((mouse_uv_x, mouse_uv_y))

        # Get evaluated version of the object
        eval_obj = self.create_eval_obj(context, obj)
        
        face, _, loop_start = find_face_from_uv(eval_obj, uv_coord)
        if not face:
            return None

        normal = face.normal
        if context.window_manager.coloraide_normal.space == 'TANGENT':
            normal = get_tangent_space_normal(eval_obj, loop_start, normal)

        return normal_to_color(normal)

    def sample_normal(self, context, event):
        """Sample normal based on current editor type"""
        area = context.area
        if area.type == 'VIEW_3D':
            return self.sample_normal_from_3d_view(context, event)
        elif area.type == 'IMAGE_EDITOR':
            return self.sample_normal_from_uv_editor(context, event)
        return None

    def update_colors(self, context, color):
        """Update color across UI and brushes"""
        if not color:
            return
            
        sync_all(context, 'picker', color)

    def modal(self, context, event):
        if not context.window_manager.coloraide_normal.enabled:
            context.window.cursor_modal_restore()
            return {'CANCELLED'}

        area = context.area
        if not area or area.type not in {'VIEW_3D', 'IMAGE_EDITOR'}:
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            if (0 <= event.mouse_x - area.x <= area.width and 
                0 <= event.mouse_y - area.y <= area.height):
                color = self.sample_normal(context, event)
                if color:
                    self.update_colors(context, color)
                    area.tag_redraw()

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                color = self.sample_normal(context, event)
                if color:
                    self.update_colors(context, color)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window.cursor_modal_restore()
            context.window_manager.coloraide_normal.enabled = False
            return {'CANCELLED'}

        return {'PASS_THROUGH'}