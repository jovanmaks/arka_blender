import bpy

class DimensionEntry(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    width: bpy.props.FloatProperty(name="Width")
    height: bpy.props.FloatProperty(name="Height")
    length: bpy.props.FloatProperty(name="Length")
    unique_id: bpy.props.StringProperty(name="Unique ID")

def register():
    bpy.utils.register_class(DimensionEntry)
    bpy.types.Scene.dimension_entries = bpy.props.CollectionProperty(type=DimensionEntry)

def unregister():
    bpy.utils.unregister_class(DimensionEntry)
    del bpy.types.Scene.dimension_entries
