"""
Operator for sampling object or tangent space normals as colors.
"""

import bpy
import gpu
from bpy.types import Operator
from mathutils import Vector, Matrix
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

class BRUSH_OT_sample_normal(Operator):
    """Sample mesh normals as colors for painting"""
    bl_idname = "brush.sample_normal"
    bl_label = "Sample Normal as Color"
    bl_description = "Sample normals as colors for painting"
    bl_options = {'REGISTER'}
    
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
    
    def create_eval_obj(self, context, obj):
        """Create evaluated version of object with modifiers applied"""
        depsgraph = context.evaluated_depsgraph_get()
        return obj.evaluated_get(depsgraph)
    
    def sample_normal_from_view(self, context, event):
        """Sample normal using view raycast with robust error handling"""
        try:
            # Check for active object
            obj = context.active_object
            if not obj or not obj.data or obj.type != 'MESH':
                self.report({'WARNING'}, "No active mesh object selected")
                return None
            
            # Check for region data
            region = context.region
            rv3d = context.region_data
            if not region or not rv3d:
                self.report({'WARNING'}, "No valid 3D view region found")
                return None
            
            # Get mouse position and view direction
            try:
                coord = event.mouse_region_x, event.mouse_region_y
                view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
                ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            except Exception as e:
                self.report({'ERROR'}, f"Failed to calculate view ray: {str(e)}")
                return None
            
            # Get evaluated version of object
            try:
                depsgraph = context.evaluated_depsgraph_get()
                eval_obj = obj.evaluated_get(depsgraph)
                matrix = eval_obj.matrix_world
                matrix_inv = matrix.inverted()
            except Exception as e:
                self.report({'ERROR'}, f"Failed to evaluate object: {str(e)}")
                return None
            
            # Calculate ray for casting
            ray_target = ray_origin + view_vector * 1000.0
            local_ray_origin = matrix_inv @ ray_origin
            local_ray_target = matrix_inv @ ray_target
            local_ray_direction = (local_ray_target - local_ray_origin).normalized()
            
            # Cast ray
            success, location, normal, face_index = eval_obj.ray_cast(
                local_ray_origin, 
                local_ray_direction
            )
            
            if not success:
                return None
                
            # Get normal in requested space
            try:
                eval_mesh = eval_obj.data
                if face_index >= len(eval_mesh.polygons):
                    self.report({'WARNING'}, "Invalid face index")
                    final_normal = normal
                else:
                    loop_index = eval_mesh.polygons[face_index].loop_start
                    final_normal = self.get_surface_normal(
                        context, 
                        eval_obj, 
                        location, 
                        normal, 
                        loop_index
                    )
                    
                return self.normal_to_color(final_normal)
                
            except Exception as e:
                self.report({'ERROR'}, f"Failed to process normal: {str(e)}")
                return None
                
        except Exception as e:
            self.report({'ERROR'}, f"Error sampling normal: {str(e)}")
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
        if not context.window_manager.coloraide_normal.enabled:
            context.window.cursor_modal_restore()
            return {'CANCELLED'}

        if event.type == 'MOUSEMOVE':
            if (0 <= event.mouse_x - context.area.x <= context.area.width and 
                0 <= event.mouse_y - context.area.y <= context.area.height):
                color = self.sample_normal_from_view(context, event)
                if color:
                    self.update_colors(context, color)

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                color = self.sample_normal_from_view(context, event)
                if color:
                    self.update_colors(context, color)
                    if hasattr(context.window_manager, 'coloraide_history'):
                        context.window_manager.coloraide_history.add_color(color)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window.cursor_modal_restore()
            context.window_manager.coloraide_normal.enabled = False
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def cleanup(self, context):
        context.window.cursor_modal_restore()
        if hasattr(self, '_handler'):
            self._handler = None
        context.window_manager.coloraide_normal.enabled = False
    
    @classmethod
    def poll(cls, context):
        if not context.active_object or not context.active_object.type == 'MESH':
            return False
        if context.mode not in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_WEIGHT'}:
            return False
        return True
    
    
def register():
    bpy.utils.register_class(BRUSH_OT_sample_normal)

def unregister():
    bpy.utils.unregister_class(BRUSH_OT_sample_normal)