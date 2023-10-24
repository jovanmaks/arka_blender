import bpy

class DimensionEntry(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    width: bpy.props.FloatProperty(name="Width")
    height: bpy.props.FloatProperty(name="Height")
    length: bpy.props.FloatProperty(name="Length")
    unique_id: bpy.props.StringProperty(name="Unique ID")


      # New toggle states
    is_toggled_1: bpy.props.BoolProperty(name="Is Long 1")
    is_toggled_2: bpy.props.BoolProperty(name="Is Long 2")
    is_toggled_3: bpy.props.BoolProperty(name="Is Short 1")
    is_toggled_4: bpy.props.BoolProperty(name="Is Short 2")
 

def register():
    bpy.utils.register_class(DimensionEntry)
    bpy.types.Scene.dimension_entries = bpy.props.CollectionProperty(type=DimensionEntry)
    bpy.types.Scene.dimension_entries_index = bpy.props.IntProperty(name="Dimension Index")

def unregister():
    bpy.utils.unregister_class(DimensionEntry)
    del bpy.types.Scene.dimension_entries
    del bpy.types.Scene.dimension_entries_index
