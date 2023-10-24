import bpy

# Custom UI List
class SimpleUlDimensions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        sorted_dims = sorted([item.width, item.height, item.length], reverse=True)
        sorted_dims = [round(x, 2) for x in sorted_dims]
        
        layout = layout.split(factor=0.8)
        row = layout.row()
        row.label(text=f"{item.name}")
        row.label(text=f"{sorted_dims[0]:.2f}")
        row.label(text=f"{sorted_dims[1]:.2f}")
        row.label(text=f"{sorted_dims[2]:.2f}")

        for i in range(1, 5):
            is_toggled = getattr(item, f'is_toggled_{i}')
            toggle_icon = "SEQUENCE_COLOR_04" if is_toggled else "SEQUENCE_COLOR_09"
            
            label_text = "Long" if i <= 2 else "Short"

            toggle_op = row.operator("object.toggle_entry", icon=toggle_icon, text=label_text)
            toggle_op.index = index
            toggle_op.toggle_id = i

        remove_op = layout.operator("object.remove_dimension", text="X")
        remove_op.index = index


# Panel
class SimplePanel(bpy.types.Panel):
    bl_label = "Dimension Panel"
    bl_idname = "PT_DimensionPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "project_name", text="Project")

        row = layout.row()
        row.prop(context.scene, "material_name", text="Material")

        layout.separator()

        row = layout.row(align=True)
        row.operator("object.get_dimension")
        row.operator("object.regenerate_dimensions")
        row.operator("object.clear_all_dimensions")

        layout.separator()

        row = layout.row()
        row.template_list("SimpleUlDimensions", "", context.scene, "dimension_entries", context.scene, "dimension_entries_index", rows=7)

        row = layout.row(align=True)
        row.operator("object.export_csv")

        row = layout.row()
        row.prop(context.scene, "container_width", text="Container Width")
        row.prop(context.scene, "container_height", text="Container Height")
        
        row = layout.row(align=True)
        row.operator("object.run_project_objects")
        row.operator("object.run_nesting_algorithm")



def register():
    bpy.utils.register_class(SimpleUlDimensions)
    bpy.utils.register_class(SimplePanel)

    bpy.types.Scene.project_name = bpy.props.StringProperty(name="Project")
    bpy.types.Scene.material_name = bpy.props.StringProperty(name="Material")


    bpy.types.Scene.container_width = bpy.props.IntProperty(name="Container Width")
    bpy.types.Scene.container_height = bpy.props.IntProperty(name="Container Height")

def unregister():
    bpy.utils.unregister_class(SimplePanel)
    bpy.utils.unregister_class(SimpleUlDimensions)
    del bpy.types.Scene.project_name
    del bpy.types.Scene.material_name


    del bpy.types.Scene.container_width
    del bpy.types.Scene.container_height

if __name__ == "__main__":
    register()


