"""
BRUSH_OT_normal_color_picker.py
Operator for sampling object or tangent space normals as colors for painting in both 3D and UV space
"""

import bpy
import gpu
import numpy as np
from mathutils import Vector, Matrix
from bpy.props import BoolProperty, EnumProperty, FloatVectorProperty
from bpy_extras import view3d_utils

def normal_to_color(normal):
    """Convert a normal vector to RGB color values"""
    return tuple((n + 1.0) * 0.5 for n in normal)

def get_tangent_space_normal(obj, loop_index, normal):
    """Convert object space normal to tangent space using active UV map"""
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

def find_face_from_uv(obj, uv_coord):
    """Find face and barycentric coordinates from UV coordinate"""
    mesh = obj.data
    if not mesh.uv_layers.active:
        return None, None, None
        
    for poly in mesh.polygons:
        uvs = [mesh.uv_layers.active.data[loop_idx].uv for loop_idx in poly.loop_indices]
        
        if len(uvs) == 3:
            bary_coord = barycentric_coordinates_2d(uv_coord, uvs[0], uvs[1], uvs[2])
            if all(0 <= x <= 1 for x in bary_coord):
                return poly, bary_coord, poly.loop_indices[0]
                
        elif len(uvs) == 4:
            tris = [(uvs[0], uvs[1], uvs[2]), (uvs[2], uvs[3], uvs[0])]
            for i, tri in enumerate(tris):
                bary_coord = barycentric_coordinates_2d(uv_coord, tri[0], tri[1], tri[2])
                if all(0 <= x <= 1 for x in bary_coord):
                    return poly, bary_coord, poly.loop_indices[0]
    
    return None, None, None

def barycentric_coordinates_2d(p, a, b, c):
    """Calculate barycentric coordinates of point p relative to triangle abc"""
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
        return (-1, -1, -1)
        
    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1.0 - v - w
    
    return (u, v, w)

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
            if not obj.data.uv_layers:
                self.report({'WARNING'}, "Object needs UV map for tangent space normals")
                return normal
            return get_tangent_space_normal(obj, loop_index, normal)
        else:
            return normal

    def create_eval_obj(self, context, obj):
        """Create an evaluated version of the object with modifiers applied"""
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

        mouse_uv_x = (event.mouse_region_x - region.x) / region.width
        mouse_uv_y = (event.mouse_region_y - region.y) / region.height
        uv_coord = Vector((mouse_uv_x, mouse_uv_y))

        # Get evaluated version of the object
        eval_obj = self.create_eval_obj(context, obj)
        
        face, bary_coords, loop_start = find_face_from_uv(eval_obj, uv_coord)
        if not face:
            return None

        normal = face.normal
        if context.window_manager.normal_picker.space == 'TANGENT':
            normal = get_tangent_space_normal(eval_obj, loop_start, normal)

        return normal_to_color(normal)

    def sample_normal_at_mouse(self, context, event):
        """Sample normal based on current editor type"""
        area = context.area
        if area.type == 'VIEW_3D':
            return self.sample_normal_from_3d_view(context, event)
        elif area.type == 'IMAGE_EDITOR':
            return self.sample_normal_from_uv_editor(context, event)
        return None

    def update_colors(self, context, color):
        """Update all color properties with the given color"""
        if not color:
            return
            
        ts = context.tool_settings
        if hasattr(ts, 'image_paint') and ts.image_paint.brush:
            ts.image_paint.brush.color = color
            if ts.unified_paint_settings.use_unified_color:
                ts.unified_paint_settings.color = color
        
        wm = context.window_manager
        wm.coloraide_picker.mean = color
        wm.coloraide_picker.current = color
        wm.coloraide_wheel.color = (*color, 1.0)

    def modal(self, context, event):
        if not context.window_manager.normal_picker.enabled:
            if context.window:
                context.window.cursor_modal_restore()
            return {'CANCELLED'}

        area = context.area
        if not area or area.type not in {'VIEW_3D', 'IMAGE_EDITOR'}:
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            if (0 <= event.mouse_x - area.x <= area.width and 
                0 <= event.mouse_y - area.y <= area.height):
                color = self.sample_normal_at_mouse(context, event)
                if color:
                    self.update_colors(context, color)
                area.tag_redraw()

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
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