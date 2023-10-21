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
        row.label(text="Toggle")
        row.label(text="Remove")

        sorted_entries = sorted(context.scene.dimension_entries, key=lambda x: x.length, reverse=True)

        for index, entry in enumerate(sorted_entries):

            row = layout.row(align=True)

            row.scale_x = 0.2  # You can set the scaling factor for the row
            row.label(text=f"{entry.name}")

            row.scale_x = 0.2
            row.label(text=f"{entry.width:.2f}")

            row.scale_x = 0.2
            row.label(text=f"{entry.height:.2f}")

            row.scale_x = 0.2
            row.label(text=f"{entry.length:.2f}")

            row.scale_x = 0.2

            original_index = next((i for i, e in enumerate(context.scene.dimension_entries) if e.unique_id == entry.unique_id), None)

            # remove_op = row.operator("object.remove_dimension", text="X")
            # remove_op.index = index

            if original_index is not None:
                remove_op = row.operator("object.remove_dimension", text="X")
                remove_op.index = original_index

            #  # Toggle button with icon
            # row.scale_x = 0.2
            # toggle_icon = 'CHECKBOX_HLT' if entry.is_toggled else 'CHECKBOX_DEHLT'
            # toggle_op = row.operator("object.toggle_entry", text="", icon=toggle_icon)
            # toggle_op.index = original_index


             # Toggle button
            row.scale_x = 0.2
            toggle_text = "On" if entry.is_toggled else "Off"
            toggle_op = row.operator("object.toggle_entry", text=toggle_text)
            toggle_op.index = original_index  # Send the original_index to the operator to know which entry to toggle


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
