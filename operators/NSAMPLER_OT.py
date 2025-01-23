"""
Operator for sampling object or tangent space normals as colors.
"""

import bpy
import gpu
from bpy.types import Operator
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils
from ..COLORAIDE_sync import sync_all
from ..COLORAIDE_utils import is_updating, UpdateFlags

def normal_to_color(normal):
    """Convert a normal vector to RGB color values"""
    return tuple((n + 1.0) * 0.5 for n in normal)

class BRUSH_OT_sample_normal(Operator):
    """Sample mesh normals as colors for painting"""
    bl_idname = "brush.sample_normal"
    bl_label = "Sample Normal as Color"
    bl_description = "Sample normals as colors for painting"
    bl_options = {'REGISTER'}
    
    @classmethod
    def poll(cls, context):
        if context.area.type not in {'VIEW_3D', 'IMAGE_EDITOR'}:
            return False
            
        if context.mode not in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_GPENCIL'}:
            return False
            
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.data.uv_layers
    
    def modal(self, context, event):
        if not context.window_manager.coloraide_normal.enabled:
            context.window.cursor_modal_restore()
            return {'CANCELLED'}

        if event.type == 'MOUSEMOVE':
            if (0 <= event.mouse_x - context.area.x <= context.area.width and 
                0 <= event.mouse_y - context.area.y <= context.area.height):
                color = self.sample_normal_from_view(context, event)
                if color and not is_updating('normal'):
                    sync_all(context, 'normal', color)

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                color = self.sample_normal_from_view(context, event)
                if color and not is_updating('normal'):
                    sync_all(context, 'normal', color)
                    if hasattr(context.window_manager, 'coloraide_history'):
                        context.window_manager.coloraide_history.add_color(color)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window.cursor_modal_restore()
            context.window_manager.coloraide_normal.enabled = False
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

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
        else:
            return normal
    
    def sample_normal_from_view(self, context, event):
        """Sample normal using view raycast"""
        try:
            # Get the object and check if it's valid
            obj = context.active_object
            if not obj or not obj.data or obj.type != 'MESH':
                self.report({'WARNING'}, "No active mesh object selected")
                return None

            # Handle different editor types
            if context.area.type == 'IMAGE_EDITOR':
                return self.sample_normal_from_uv(context, event)
            else:
                return self.sample_normal_from_3d_view(context, event)

        except Exception as e:
            self.report({'ERROR'}, f"Error sampling normal: {str(e)}")
            return None

    def sample_normal_from_3d_view(self, context, event):
        """Sample normal using 3D view raycast"""
        try:
            obj = context.active_object
            if not obj or not obj.data or obj.type != 'MESH':
                return None

            if not context.region_data:
                return None
                
            region = context.region
            rv3d = context.region_data
            coord = event.mouse_region_x, event.mouse_region_y
            
            # Get ray details
            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            ray_target = ray_origin + view_vector * 1000.0

            # Get object space ray
            matrix = obj.matrix_world
            matrix_inv = matrix.inverted()
            ray_origin_obj = matrix_inv @ ray_origin
            ray_target_obj = matrix_inv @ ray_target
            ray_direction_obj = (ray_target_obj - ray_origin_obj).normalized()

            # Cast ray
            success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)
            
            if success:
                mesh = obj.data
                loop_index = mesh.polygons[face_index].loop_start
                final_normal = self.get_surface_normal(context, obj, location, normal, loop_index)
                return normal_to_color(final_normal)
                
            return None

        except Exception as e:
            self.report({'ERROR'}, f"Error sampling normal: {str(e)}")
            return None

    def sample_normal_from_uv(self, context, event):
        """Sample normal using UV coordinates"""
        try:
            obj = context.active_object
            mesh = obj.data
            
            if not mesh.uv_layers.active:
                self.report({'WARNING'}, "No active UV map")
                return None
                
            region = context.region
            uv_data = mesh.uv_layers.active.data
            
            # Convert mouse coordinates to UV space
            x = (event.mouse_region_x - region.x) / region.width
            y = (event.mouse_region_y - region.y) / region.height
            
            # Find the face that contains these UV coordinates
            for poly in mesh.polygons:
                uvs = [uv_data[loop_idx].uv for loop_idx in poly.loop_indices]
                if point_in_polygon((x, y), uvs):
                    normal = poly.normal
                    if context.window_manager.coloraide_normal.space == 'TANGENT':
                        normal = self.get_surface_normal(context, obj, None, normal, poly.loop_start)
                    return normal_to_color(normal)
                    
            return None

        except Exception as e:
            self.report({'ERROR'}, f"Error sampling UV normal: {str(e)}")
            return None

def point_in_polygon(point, polygon):
    """Check if a point is inside a polygon using ray casting"""
    x, y = point
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        if (((polygon[i][1] > y) != (polygon[j][1] > y)) and
            (x < (polygon[j][0] - polygon[i][0]) * (y - polygon[i][1]) /
            (polygon[j][1] - polygon[i][1]) + polygon[i][0])):
            inside = not inside
        j = i
        
    return inside

def get_tangent_space_normal(obj, loop_index, normal):
    """Convert a normal to tangent space using UV map data"""
    mesh = obj.data
    
    if not mesh.uv_layers.active:
        return normal
        
    if not mesh.loops[loop_index].tangent:
        mesh.calc_tangents()
    
    loop = mesh.loops[loop_index]
    tangent = Vector(loop.tangent)
    bitangent = Vector(loop.bitangent)
    normal_vec = Vector(normal)
    
    tangent_matrix = Matrix([tangent, bitangent, normal_vec]).transposed()
    return tangent_matrix @ normal_vec

def register():
    bpy.utils.register_class(BRUSH_OT_sample_normal)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_sample_normal)