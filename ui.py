import bpy
# from .rectpack.packer import PackingMode  

# Define the options for each EnumProperty
mode_items = [
    ('PackingMode.Offline', "Offline", "PackingMode.Offline"),
    # ('PackingMode.Online', "Online", "PackingMode.Online")
]

bin_algo_items = [
    ('BNF', "Bin Next Fit", "PackingBin.BNF"),
    ('BFF', "Bin First Fit", "PackingBin.BFF"),
    ('BBF', "Bin Best Fit", "PackingBin.BBF"),
    ('Global', "Global", "PackingBin.Global")
]

pack_algo_items = [
    # MaxRects variants
    ('MaxRectsBl', "MaxRects Bottom-Left", "MaxRectsBl"),
    ('MaxRectsBssf', "MaxRects Best Short Side Fit", "MaxRectsBssf"),
    ('MaxRectsBaf', "MaxRects Best Area Fit", "MaxRectsBaf"),
    ('MaxRectsBlsf', "MaxRects Best Long Side Fit", "MaxRectsBlsf"),
    # Skyline variants
    ('SkylineBl', "Skyline Bottom-Left", "SkylineBl"),
    ('SkylineBlWm', "Skyline Bottom-Left WasteMap", "SkylineBlWm"),
    ('SkylineMwf', "Skyline Min Waste Fit", "SkylineMwf"),
    ('SkylineMwfl', "Skyline Min Waste Fit Level", "SkylineMwfl"),
    ('SkylineMwfWm', "Skyline Min Waste Fit WasteMap", "SkylineMwfWm"),
    ('SkylineMwflWm', "Skyline Min Waste Fit Level WasteMap", "SkylineMwflWm"),
    # Guillotine variants
    ('GuillotineBssfSas', "Guillotine BSSF Split Shorter Axis", "GuillotineBssfSas"),
    ('GuillotineBssfLas', "Guillotine BSSF Split Longer Axis", "GuillotineBssfLas"),
    ('GuillotineBssfSlas', "Guillotine BSSF Split Longer Axis Shorter Leftover", "GuillotineBssfSlas"),
    ('GuillotineBssfLlas', "Guillotine BSSF Split Longer Axis Longer Leftover", "GuillotineBssfLlas"),
    ('GuillotineBssfMaxas', "Guillotine BSSF Split Max Axis", "GuillotineBssfMaxas"),
    ('GuillotineBssfMinas', "Guillotine BSSF Split Min Axis", "GuillotineBssfMinas"),
    ('GuillotineBlsfSas', "Guillotine BLSF Split Shorter Axis", "GuillotineBlsfSas"),
    ('GuillotineBlsfLas', "Guillotine BLSF Split Longer Axis", "GuillotineBlsfLas"),
    ('GuillotineBlsfSlas', "Guillotine BLSF Split Longer Axis Shorter Leftover", "GuillotineBlsfSlas"),
    ('GuillotineBlsfLlas', "Guillotine BLSF Split Longer Axis Longer Leftover", "GuillotineBlsfLlas"),
    ('GuillotineBlsfMaxas', "Guillotine BLSF Split Max Axis", "GuillotineBlsfMaxas"),
    ('GuillotineBlsfMinas', "Guillotine BLSF Split Min Axis", "GuillotineBlsfMinas"),
    ('GuillotineBafSas', "Guillotine BAF Split Shorter Axis", "GuillotineBafSas"),
    ('GuillotineBafLas', "Guillotine BAF Split Longer Axis", "GuillotineBafLas"),
    ('GuillotineBafSlas', "Guillotine BAF Split Longer Axis Shorter Leftover", "GuillotineBafSlas"),
    ('GuillotineBafLlas', "Guillotine BAF Split Longer Axis Longer Leftover", "GuillotineBafLlas"),
    ('GuillotineBafMaxas', "Guillotine BAF Split Max Axis", "GuillotineBafMaxas"),
    ('GuillotineBafMinas', "Guillotine BAF Split Min Axis", "GuillotineBafMinas"),
]

sort_algo_items = [
    ('SORT_NONE', "None", "SORT_NONE"),
    ('SORT_AREA', "Area", "SORT_AREA"),
    ('SORT_PERI', "Perimeter", "SORT_PERI"),
    ('SORT_DIFF', "Difference", "SORT_DIFF"),
    ('SORT_SSIDE', "Short Side", "SORT_SSIDE"),
    ('SORT_LSIDE', "Long Side", "SORT_LSIDE"),
    ('SORT_RATIO', "Ratio", "SORT_RATIO")
]

rotation_items = [
    ('ENABLED', "Enabled", "Enable rotation"),
    ('DISABLED', "Disabled", "Disable rotation")
]

# Custom UI List
class SimpleUlDimensions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        sorted_dims = sorted([item.width, item.height, item.length], reverse=True)
        sorted_dims = [round(x, 2) for x in sorted_dims]
        
        # Split the layout and add the index as a label
        layout = layout.split(factor=0.8)
        row = layout.row()
        row.label(text=f"{index + 1}")  # Add +1 to index for human-readable numbering (starting from 1)
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
    bl_category = 'Arka'

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


        row = layout.row()
        row.prop(context.scene, "container_width", text="Container Width(cm)")
        row.prop(context.scene, "container_height", text="Container Height(cm)")
        row.prop(context.scene, "spacing", text="Spacing")
        

        layout.separator()
        layout.label(text="Packing Options:")

        # Dropdown for mode
        row = layout.row()
        row.prop(context.scene, "packing_mode", text="Mode")

        # Dropdown for bin_algo
        row = layout.row()
        row.prop(context.scene, "bin_algo", text="Bin Algorithm")

        # Dropdown for pack_algo
        row = layout.row()
        row.prop(context.scene, "pack_algo", text="Packing Algorithm")

        # Dropdown for sort_algo
        row = layout.row()
        row.prop(context.scene, "sort_algo", text="Sort Algorithm")

        # Dropdown for rotation
        row = layout.row()
        row.prop(context.scene, "rotation", text="Rotation")
        layout.separator()

        row = layout.row(align=True)
        row.operator("object.run_project_objects")
        row.operator("object.run_nesting_algorithm")

        row = layout.row(align=True)
        row.operator("object.export_csv")
        row.operator("object.stickers_operator")
        layout.operator("object.export_canvas_as_pdf", text="Canvas")
        # row.operator("object.export_canvas")


def register():
    bpy.utils.register_class(SimpleUlDimensions)
    bpy.utils.register_class(SimplePanel)

    bpy.types.Scene.project_name = bpy.props.StringProperty(name="Project")
    bpy.types.Scene.material_name = bpy.props.StringProperty(name="Material")
    bpy.types.Scene.spacing = bpy.props.IntProperty(name="Spacing")


    bpy.types.Scene.container_width = bpy.props.IntProperty(name="Container Width")
    bpy.types.Scene.container_height = bpy.props.IntProperty(name="Container Height")

    bpy.types.Scene.packing_mode = bpy.props.EnumProperty(items=mode_items)
    bpy.types.Scene.bin_algo = bpy.props.EnumProperty(items=bin_algo_items)
    bpy.types.Scene.pack_algo = bpy.props.EnumProperty(items=pack_algo_items)
    bpy.types.Scene.sort_algo = bpy.props.EnumProperty(items=sort_algo_items)
    bpy.types.Scene.rotation = bpy.props.EnumProperty(items=rotation_items)


def unregister():
    bpy.utils.unregister_class(SimplePanel)
    bpy.utils.unregister_class(SimpleUlDimensions)

    del bpy.types.Scene.project_name
    del bpy.types.Scene.material_name
    del bpy.types.Scene.spacing


    del bpy.types.Scene.container_width
    del bpy.types.Scene.container_height

    del bpy.types.Scene.packing_mode
    del bpy.types.Scene.bin_algo
    del bpy.types.Scene.pack_algo
    del bpy.types.Scene.sort_algo
    del bpy.types.Scene.rotation


if __name__ == "__main__":
    register()


