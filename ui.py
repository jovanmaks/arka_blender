import bpy

class SimplePanel(bpy.types.Panel):
    bl_label = "Dimension Panel"
    bl_idname = "PT_DimensionPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Name")
        row.label(text="Width")
        row.label(text="Height")
        row.label(text="Length")
        row.label(text="Remove")

        for index, entry in enumerate(context.scene.dimension_entries):
            row = layout.row(align=True)
        
            split = row.split(factor=0.2)
            split.label(text=f"{entry.name}")

            split = row.split(factor=0.2)
            split.label(text=f"{entry.width}")

            split = row.split(factor=0.2)
            split.label(text=f"{entry.height}")

            split = row.split(factor=0.2)
            split.label(text=f"{entry.length}")

            split = row.split(factor=0.2)
            remove_op = split.operator("object.remove_dimension", text="X")  # <-- Add button
            remove_op.index = index  # <-- Set the index to remove

        layout.operator("object.get_dimension")
        layout.operator("object.regenerate_dimensions")
        layout.operator("object.export_csv")
        layout.operator("object.clear_all_dimensions")

def register():
    bpy.utils.register_class(SimplePanel)

def unregister():
    bpy.utils.unregister_class(SimplePanel)
