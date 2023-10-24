import bpy

class SimplePanel(bpy.types.Panel):
    bl_label = "Dimension Panel"
    bl_idname = "PT_DimensionPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'



    def draw(self, context):
        layout = self.layout

        # col = layout.column(align=True)
        # col.prop(context.scene, "project_name", text="Project Name")
        # col.prop(context.scene, "material_name", text="Material")


        row = layout.row()
        row.prop(context.scene, "project_name", text="Project")
        
        row = layout.row()
        row.prop(context.scene, "material_name", text="Material")



        layout.separator()

        row = layout.row(align=True)
        row.operator("object.get_dimension")
        row.operator("object.regenerate_dimensions")
        row.operator("object.clear_all_dimensions")


        row = layout.row()
        row.label(text="Name")  
        row.label(text="Long")
        row.label(text="Short")
        row.label(text="Thick")
        row.label(text="Long 1")
        row.label(text="Long 2")
        row.label(text="Short 1")
        row.label(text="Short 2")
        row.label(text="Remove")

        sorted_entries = sorted(context.scene.dimension_entries, key=lambda x: x.length, reverse=True)

        for index, entry in enumerate(sorted_entries):

            sorted_dims = sorted([entry.width, entry.height, entry.length], reverse=True)
            sorted_dims = [round(x, 2) for x in sorted_dims]
        

            row = layout.row(align=True)

            row.scale_x = 0.2  # You can set the scaling factor for the row
            row.label(text=f"{entry.name}")

            row.scale_x = 0.2
            row.label(text=f"{sorted_dims[0]:.2f}")  # Long

            row.scale_x = 0.2
            row.label(text=f"{sorted_dims[1]:.2f}")  # Middle

            row.scale_x = 0.2
            row.label(text=f"{sorted_dims[2]:.2f}")  # Short

            row.scale_x = 0.2

            original_index = next((i for i, e in enumerate(context.scene.dimension_entries) if e.unique_id == entry.unique_id), None)

            # remove_op = row.operator("object.remove_dimension", text="X")
            # remove_op.index = index


        
            # Toggle button
            row.scale_x = 0.2
            for i in range(1, 5):
                toggle_text = "YES" if getattr(entry, f'is_toggled_{i}') else "NO"
                toggle_op = row.operator("object.toggle_entry", text=toggle_text)
                toggle_op.index = original_index
                toggle_op.toggle_id = i

            # Remove button
            if original_index is not None:
                row.scale_x = 0.2
                remove_op = row.operator("object.remove_dimension", text="X")
                remove_op.index = original_index



        row = layout.row(align=True)
        row.operator("object.export_csv")

def register():
    bpy.utils.register_class(SimplePanel)
    bpy.types.Scene.project_name = bpy.props.StringProperty(name="Project")
    bpy.types.Scene.material_name = bpy.props.StringProperty(name="Material")

def unregister():
    bpy.utils.unregister_class(SimplePanel)
    del bpy.types.Scene.project_name
    del bpy.types.Scene.material_name
