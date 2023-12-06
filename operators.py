import bpy
import csv
import os
import sys

# Assuming this script is in the root directory of your plugin
plugin_path = os.path.dirname(os.path.realpath(__file__))
pyfpdf_path = os.path.join(plugin_path, 'pyfpdf-binary')

# Add the pyfpdf path to sys.path
if pyfpdf_path not in sys.path:
    sys.path.append(pyfpdf_path)

# Now you can import FPDF
from fpdf import FPDF


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
    bl_label = "Get"

    def execute(self, context):
        

        for obj in bpy.context.selected_objects:
            if obj is not None and obj.type == 'MESH':
                unique_id = str(hash(obj))

                # Check if this unique_id already exists in the collection
                if any(entry.unique_id == unique_id for entry in context.scene.dimension_entries):
                    self.report({'WARNING'}, f"{obj.name} is already in the list.")
                    continue

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
    bl_label = "Reload"

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




class ToggleEntryOperator(bpy.types.Operator):
    bl_idname = "object.toggle_entry"
    bl_label = "Edge"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()
    toggle_id: bpy.props.IntProperty()

    def execute(self, context):
        toggle_attr = f'is_toggled_{self.toggle_id}'
        if hasattr(context.scene.dimension_entries[self.index], toggle_attr):
            current_state = getattr(context.scene.dimension_entries[self.index], toggle_attr)
            setattr(context.scene.dimension_entries[self.index], toggle_attr, not current_state)
        return {'FINISHED'}

class ExportCSVOperator(bpy.types.Operator):
    bl_idname = "object.export_csv"
    bl_label = "CSV"
    
    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH",
        name="Save As",
        description="Save dimensions to CSV",
        default="name.csv"  
    )

    def execute(self, context):
        

        with open(self.filepath, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)

            # Write the header with an extra 'Material' column
            csvwriter.writerow([ 'Name', 'Longer', 'Shorter', 'Thickness', 'Edges', 'Material'])

            # Write the dimensions
            for entry in context.scene.dimension_entries:
                sorted_dims = sorted([entry.width, entry.height, entry.length], reverse=True)
                sorted_dims = [round(x, 2) for x in sorted_dims]

                kant_value = ""
                for i in range(1, 5):
                    if getattr(entry, f'is_toggled_{i}'):
                        kant_value += "S" if i > 2 else "L"

                # Use the material name from the UI
                material_name = context.scene.material_name

                csvwriter.writerow([ entry.name, *sorted_dims, kant_value, material_name])

        self.report({'INFO'}, f"Dimensions exported to {self.filepath}")

        return {'FINISHED'}


    def invoke(self, context, event):
        # Use the project name as the default filepath
        self.filepath = f"{context.scene.project_name}.csv"
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class StickersOperator(bpy.types.Operator):
    bl_idname = "object.stickers_operator"
    bl_label = "Stickers"
    bl_description = "Export stickers as PDFs"

    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH",
        name="Save As",
        description="Save stickers to PDF",
        default="//untitled.pdf"
    )

    def draw_and_export_pdf(self, original_width, original_height, filename):
        """
        Create a PDF file with a white B6 page and a centered rectangle.
        """
        # B6 size in mm
        b6_width, b6_height = 176, 125

        # Calculate scale to fit the rectangle inside B6 size
        scale = min(b6_width / original_width, b6_height / original_height)
        scaled_width, scaled_height = original_width * scale, original_height * scale

        # Calculate position to center the rectangle
        x_pos = (b6_width - scaled_width) / 2
        y_pos = (b6_height - scaled_height) / 2

        pdf = FPDF(unit="mm", format=[b6_width, b6_height])
        pdf.add_page()

         # Set fill color for the rectangle
        pdf.set_fill_color(0, 255, 0)  # Black color for the rectangle
        
      # Draw the centered rectangle (without covering the entire page)
        pdf.rect(x_pos, y_pos, scaled_width, scaled_height, 'F')

        # Save the PDF
        pdf.output(filename)

    def execute(self, context):
        pdf_dir = bpy.path.abspath(self.filepath)
        os.makedirs(pdf_dir, exist_ok=True)

        for entry in context.scene.dimension_entries:
            width, height = entry.width, entry.height
            pdf_filename = os.path.join(pdf_dir, f"{entry.name}.pdf")
            self.draw_and_export_pdf(width, height, pdf_filename)

        self.report({'INFO'}, f"Stickers exported as PDFs to {pdf_dir}")
        return {'FINISHED'}

    def invoke(self, context, event):
        # self.filepath = f"{context.scene.project_name}.pdf"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



def register():
    bpy.utils.register_class(GetDimensionOperator)
    bpy.utils.register_class(RegenerateOperator)
    bpy.utils.register_class(RemoveDimensionOperator)
    bpy.utils.register_class(ClearAllDimensionsOperator)
    bpy.utils.register_class(ExportCSVOperator)
    bpy.utils.register_class(StickersOperator)
    bpy.utils.register_class(ToggleEntryOperator)

def unregister():
    bpy.utils.unregister_class(GetDimensionOperator)
    bpy.utils.unregister_class(RegenerateOperator)
    bpy.utils.unregister_class(RemoveDimensionOperator)
    bpy.utils.unregister_class(ClearAllDimensionsOperator)
    bpy.utils.unregister_class(ExportCSVOperator)
    bpy.utils.unregister_class(StickersOperator)
    bpy.utils.unregister_class(ToggleEntryOperator)
