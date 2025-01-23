# COLORAIDE_monitor.py
import bpy
from bpy.types import Operator
from .COLORAIDE_sync import sync_all, is_updating

class COLOR_OT_monitor(Operator):
   bl_idname = "color.monitor"
   bl_label = "Monitor Color Changes"
   bl_options = {'INTERNAL'}
   
   old_color = None
   
   def modal(self, context, event):
       try:
           ts = context.tool_settings
           curr_color = None
           
           if context.mode == 'PAINT_GPENCIL' and ts.gpencil_paint.brush:
               curr_color = tuple(ts.gpencil_paint.brush.color)
           elif ts.image_paint and ts.image_paint.brush:
               curr_color = tuple(ts.image_paint.brush.color)
           
           if curr_color != self.old_color and curr_color is not None:
               if not is_updating():
                   sync_all(context, 'brush', curr_color)
               self.old_color = curr_color
               
       except Exception as e:
           print(f"Color monitor error: {e}")
           
       return {'PASS_THROUGH'}

   def invoke(self, context, event):
       context.window_manager.modal_handler_add(self)
       return {'RUNNING_MODAL'}