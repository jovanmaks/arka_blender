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

            row.scale_x = 0.2  # You can set the scaling factor for the row
            row.label(text=f"{entry.name}")

            row.scale_x = 0.2
            row.label(text=f"{entry.width}")

            row.scale_x = 0.2
            row.label(text=f"{entry.height}")

            row.scale_x = 0.2
            row.label(text=f"{entry.length}")

            row.scale_x = 0.2
            remove_op = row.operator("object.remove_dimension", text="X")
            remove_op.index = index

        layout.operator("object.get_dimension")
        layout.operator("object.regenerate_dimensions")
        layout.operator("object.export_csv")
        layout.operator("object.clear_all_dimensions")

def register():
    bpy.utils.register_class(SimplePanel)

def unregister():
    bpy.utils.unregister_class(SimplePanel)
