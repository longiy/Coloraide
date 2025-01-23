import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import PropertyGroup
from ..COLORAIDE_sync import sync_all, is_updating

class ColoraideHexProperties(PropertyGroup):
    suppress_updates: BoolProperty(default=False)
    
    def update_hex_value(self, context):
        if is_updating() or self.suppress_updates:
            return
            
        value = self.value.strip().upper()
        if not value.startswith('#'):
            value = '#' + value
            
        if value != self.value:
            self.value = value
            return
            
        sync_all(context, 'hex', self.value)

    value: StringProperty(
        name="Hex",
        default="#808080",
        maxlen=7,
        update=update_hex_value
    )