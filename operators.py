import bpy
import csv
import os

class GetDimensionOperator(bpy.types.Operator):
    # ... (rest of the code unchanged)
    bl_idname = "object.get_dimension"
    bl_label = "Get Dimensions"  #

    def execute(self, context):
        obj = bpy.context.active_object
        if obj is not None and obj.type == 'MESH':
            dimensions = obj.dimensions
            new_entry = context.scene.dimension_entries.add()
            new_entry.name = obj.name
            new_entry.width = round(dimensions.x * 100, 1)  # Convert to cm and round to 2 decimal places
            new_entry.height = round(dimensions.y * 100, 1)  # Convert to cm and round to 2 decimal places
            new_entry.length = round(dimensions.z * 100, 1)  # Convert to cm and round to 2 decimal places
        return {'FINISHED'}

class RegenerateOperator(bpy.types.Operator):
    # ... (rest of the code unchanged)
    bl_idname = "object.regenerate_dimensions"
    bl_label = "Regenerate"

    def execute(self, context):
        context.scene.dimension_entries.clear()
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                dimensions = obj.dimensions
                new_entry = context.scene.dimension_entries.add()
                new_entry.name = obj.name
                new_entry.width = round(dimensions.x * 100, 1)  # Convert to cm and round to 2 decimal places
                new_entry.height = round(dimensions.y * 100, 1)  # Convert to cm and round to 2 decimal places
                new_entry.length = round(dimensions.z * 100, 1)  # Convert to cm and round to 2 decimal places
        return {'FINISHED'}

class RemoveDimensionOperator(bpy.types.Operator):
    bl_idname = "object.remove_dimension"
    bl_label = "Remove"
    
    index: bpy.props.IntProperty()  # The index of the entry to remove
    
    def execute(self, context):
        context.scene.dimension_entries.remove(self.index)
        return {'FINISHED'}

import bpy
import csv

class ExportCSVOperator(bpy.types.Operator):
    bl_idname = "object.export_csv"
    bl_label = "Export to CSV"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # <-- Add this line for file path

    def execute(self, context):
        with open(self.filepath, 'w', newline='') as csvfile:  # Use the chosen filepath
            csvwriter = csv.writer(csvfile)
            
            # Write the header
            csvwriter.writerow(['Ime', 'Sirina', 'Visina', 'Duzina'])
            
            # Write the dimensions
            for entry in context.scene.dimension_entries:
                csvwriter.writerow([entry.name, entry.width, entry.height, entry.length])

        self.report({'INFO'}, f"Dimensions exported to {self.filepath}")
        
        return {'FINISHED'}

    def invoke(self, context, event):  # <-- Add this method for the file dialog
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



def register():
    bpy.utils.register_class(GetDimensionOperator)
    bpy.utils.register_class(RegenerateOperator)
    bpy.utils.register_class(RemoveDimensionOperator)
    bpy.utils.register_class(ExportCSVOperator)

def unregister():
    bpy.utils.unregister_class(GetDimensionOperator)
    bpy.utils.unregister_class(RegenerateOperator)
    bpy.utils.unregister_class(RemoveDimensionOperator)
    bpy.utils.unregister_class(ExportCSVOperator) 
