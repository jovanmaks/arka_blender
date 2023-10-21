import bpy
import csv
import os

def set_object_material(obj, color=(0, 1, 0, 1)):  # default color is green
    # Create a new material
    mat = bpy.data.materials.new(name="Added_Object_Material")

    # Enable 'Use nodes':
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    # Add a new Principled BSDF shader node
    shader_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    shader_node.location = (0, 0)
    shader_node.inputs[0].default_value = color  # RGBA

    # Add Material Output node and connect to shader node
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (300, 0)

    links = mat.node_tree.links
    link = links.new
    link(shader_node.outputs["BSDF"], material_output.inputs["Surface"])

    # Assign material to object
    if len(obj.data.materials):
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


class GetDimensionOperator(bpy.types.Operator):
    bl_idname = "object.get_dimension"
    bl_label = "Get"  #

    def execute(self, context):
        obj = bpy.context.active_object
        if obj is not None and obj.type == 'MESH':


            # Generate a unique ID for the object
            unique_id = str(hash(obj))
            
            # Check if this unique_id already exists in the collection
            if any(entry.unique_id == unique_id for entry in context.scene.dimension_entries):
                self.report({'WARNING'}, "This object is already in the list.")
                return {'CANCELLED'}

            # If it doesn't exist, then add it to the collection
            dimensions = obj.dimensions
            obj['unique_id'] = unique_id  # Add a custom property to the object
            new_entry = context.scene.dimension_entries.add()
            new_entry.name = obj.name
            new_entry.unique_id = unique_id
            new_entry.width = round(dimensions.x * 100, 1)
            new_entry.height = round(dimensions.y * 100, 1)
            new_entry.length = round(dimensions.z * 100, 1)


            set_object_material(obj)

        return {'FINISHED'}


class RegenerateOperator(bpy.types.Operator):
    bl_idname = "object.regenerate_dimensions"
    bl_label = "Regenerate"

    def execute(self, context):
        for entry in context.scene.dimension_entries:
            obj = next((o for o in bpy.data.objects if o.get('unique_id') == entry.unique_id), None)
            if obj and obj.type == 'MESH':
                dimensions = obj.dimensions
                entry.name = obj.name  # Update the name
                entry.width = round(dimensions.x * 100, 1)  # Convert to cm and round to 2 decimal places
                entry.height = round(dimensions.y * 100, 1)  # Convert to cm and round to 2 decimal places
                entry.length = round(dimensions.z * 100, 1)  # Convert to cm and round to 2 decimal places
        return {'FINISHED'}



class RemoveDimensionOperator(bpy.types.Operator):
    bl_idname = "object.remove_dimension"
    bl_label = "Remove"
    
    index: bpy.props.IntProperty()  # The index of the entry to remove
    
    def execute(self, context):
        entry = context.scene.dimension_entries[self.index]
        unique_id = entry.unique_id
        
        # Find object by its unique_id
        obj = next((o for o in bpy.data.objects if o.get('unique_id') == unique_id), None)
        
        # Remove material from object
        if obj and obj.type == 'MESH':
            if len(obj.data.materials) > 0:
                obj.data.materials.clear()
        
        # Remove the entry from the list
        context.scene.dimension_entries.remove(self.index)
        
        return {'FINISHED'}

class ClearAllDimensionsOperator(bpy.types.Operator):
    bl_idname = "object.clear_all_dimensions"
    bl_label = "Clear"

    def execute(self, context):
        # Loop through all entries in the list
        for entry in context.scene.dimension_entries:
            unique_id = entry.unique_id
            
            # Find object by its unique_id
            obj = next((o for o in bpy.data.objects if o.get('unique_id') == unique_id), None)
            
            # Remove material from object
            if obj and obj.type == 'MESH':
                if len(obj.data.materials) > 0:
                    obj.data.materials.clear()

        # Clear the entire list
        context.scene.dimension_entries.clear()

        return {'FINISHED'}




class ExportCSVOperator(bpy.types.Operator):
    bl_idname = "object.export_csv"
    bl_label = "CSV"
    
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
    bpy.utils.register_class(ClearAllDimensionsOperator)
    bpy.utils.register_class(ExportCSVOperator)

def unregister():
    bpy.utils.unregister_class(GetDimensionOperator)
    bpy.utils.unregister_class(RegenerateOperator)
    bpy.utils.unregister_class(RemoveDimensionOperator)
    bpy.utils.unregister_class(ClearAllDimensionsOperator)
    bpy.utils.unregister_class(ExportCSVOperator) 
