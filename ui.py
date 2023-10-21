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
        row.label(text="Long")
        row.label(text="Short")
        row.label(text="Thick")
        row.label(text="Remove")

        for index, entry in enumerate(context.scene.dimension_entries):
            # Sort the dimensions
            sorted_dims = sorted([entry.width, entry.height, entry.length], reverse=True)
            
            row = layout.row(align=True)

            row.scale_x = 0.2  # You can set the scaling factor for the row
            row.label(text=f"{entry.name}")

            # Use sorted dimensions here
            row.scale_x = 0.2
            row.label(text=f"{sorted_dims[0]:.2f}")

            row.scale_x = 0.2
            row.label(text=f"{sorted_dims[1]:.2f}")

            row.scale_x = 0.2
            row.label(text=f"{sorted_dims[2]:.2f}")

            row.scale_x = 0.2

            original_index = next((i for i, e in enumerate(context.scene.dimension_entries) if e.unique_id == entry.unique_id), None)

            if original_index is not None:
                remove_op = row.operator("object.remove_dimension", text="X")
                remove_op.index = original_index



        row = layout.row(align=True)
        row.operator("object.get_dimension")
        row.operator("object.regenerate_dimensions")

        row = layout.row(align=True)
        row.operator("object.export_csv")
        row.operator("object.clear_all_dimensions")

def register():
    bpy.utils.register_class(SimplePanel)

def unregister():
    bpy.utils.unregister_class(SimplePanel)
