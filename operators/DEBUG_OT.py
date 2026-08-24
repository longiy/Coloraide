import bpy
from bpy.types import Operator

from ..COLORAIDE_debug import LOG_NAME, clear_log


class COLOR_OT_open_debug_log(Operator):
    bl_idname = "color.open_debug_log"
    bl_label = "Open Debug Log"
    bl_description = "Open the Coloraide debug log in a Text Editor"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        text = bpy.data.texts.get(LOG_NAME)
        if text is None:
            text = bpy.data.texts.new(LOG_NAME)

        area = next((a for a in context.screen.areas if a.type == 'TEXT_EDITOR'), None)
        if area is None:
            for a in context.screen.areas:
                if a.type in {'PREFERENCES', 'PROPERTIES'}:
                    continue
                a.type = 'TEXT_EDITOR'
                area = a
                break

        if area:
            area.spaces.active.text = text
            self.report({'INFO'}, "Opened Coloraide_Debug_Log in Text Editor")
        else:
            self.report({'INFO'}, "Coloraide_Debug_Log ready - open a Text Editor to view it")
        return {'FINISHED'}


class COLOR_OT_clear_debug_log(Operator):
    bl_idname = "color.clear_debug_log"
    bl_label = "Clear Debug Log"
    bl_description = "Clear the contents of the Coloraide debug log"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        clear_log()
        self.report({'INFO'}, "Coloraide debug log cleared")
        return {'FINISHED'}
