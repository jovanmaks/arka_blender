import bpy
from collections import namedtuple
import pdb
from fpdf import FPDF

from .rectpack.packer import newPacker, PackingMode, PackingBin, SORT_RATIO # Import necessary constants
from .rectpack import packer, guillotine, maxrects, skyline


# NamedTuple to represent a rectangle
Rectangle = namedtuple("Rectangle", ["x", "y", "w", "h"])
# FreeRect to represent a free area in the container
Rect = namedtuple("Rect", ["x", "y", "w", "h"])


# Custom PropertyGroup to hold rectangle data
class PackedRectangle(bpy.types.PropertyGroup):
    x: bpy.props.FloatProperty()
    y: bpy.props.FloatProperty()
    w: bpy.props.FloatProperty()
    h: bpy.props.FloatProperty()
    rid: bpy.props.IntProperty()


class RunNestingAlgorithmOperator(bpy.types.Operator):
    bl_idname = "object.run_nesting_algorithm"
    bl_label = "Rectpack"

    def execute(self, context):
        container_width = context.scene.container_width
        container_height = context.scene.container_height
        spacing = context.scene.spacing     


        mode_str = context.scene.packing_mode
        try:
            mode = getattr(PackingMode, mode_str.split('.')[-1])
        except AttributeError:
            self.report({'ERROR'}, f"Unknown packing mode: {mode_str}")
            return {'CANCELLED'}


        bin_algo_str = context.scene.bin_algo
        try:
            bin_algo = getattr(PackingBin, bin_algo_str)
        except AttributeError:
            self.report({'ERROR'}, f"Unknown bin algorithm: {bin_algo_str}")
            return {'CANCELLED'}


        # pdb.set_trace()
        pack_algo_str = context.scene.pack_algo

        try:
            if pack_algo_str.startswith('MaxRects'):
                pack_algo = getattr(maxrects, pack_algo_str)
            elif pack_algo_str.startswith('Skyline'):
                pack_algo = getattr(skyline, pack_algo_str)
            elif pack_algo_str.startswith('Guillotine'):
                pack_algo = getattr(guillotine, pack_algo_str)
            else:
                raise AttributeError(f"Unknown packing algorithm: {pack_algo_str}")

        except AttributeError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}



        sort_algo_str = context.scene.sort_algo
        try:
            sort_algo = getattr(packer, sort_algo_str)
        except AttributeError:
            self.report({'ERROR'}, f"Unknown sort algorithm: {sort_algo_str}")
            return {'CANCELLED'} 


        rotation_str = context.scene.rotation
        if rotation_str == 'ENABLED':
            rotation = True
        elif rotation_str == 'DISABLED':
            rotation = False
        else:
            # Handle the case where rotation is neither ENABLED nor DISABLED
            self.report({'ERROR'}, f"Unknown rotation value: {rotation_str}")
            return {'CANCELLED'}
   
        # Create a new collection for the planes
        plane_collection = bpy.data.collections.new("Packed Planes")
        bpy.context.scene.collection.children.link(plane_collection)


        rectangles = []
        for index, entry in enumerate(context.scene.dimension_entries):
            sorted_dims = sorted([entry.width, entry.height, entry.length])
            rect_width_with_spacing = int(sorted_dims[1]) + spacing
            rect_height_with_spacing = int(sorted_dims[2]) + spacing
            rectangles.append((rect_width_with_spacing, rect_height_with_spacing, index))  # Add index as identifier


        packed_rectangles = set()
        bin_offset = 0
        extra_space = 0.2  # Define extra space (in Blender units)

        packed_rectangles_by_bin = {}
        bin_index = 0  # Initialize bin index


        while len(packed_rectangles) < len(rectangles):
            # pdb.set_trace()
            p = newPacker(mode=mode, bin_algo=bin_algo, pack_algo=pack_algo, sort_algo=sort_algo, rotation=rotation)
            # Add a new bin
            p.add_bin(container_width, container_height)

            # Add only the rectangles that are not yet packed and can fit in the bin
            for r in rectangles:
                if r[2] not in packed_rectangles:  # Check using identifier
                    rect_width, rect_height = r[:2]
                    if rect_width <= container_width and rect_height <= container_height:
                        p.add_rect(rect_width, rect_height, rid=r[2])  # Pass width, height, and identifier
                    else:
                        # Handle the case where the rectangle is too big
                        # For example, report an error or skip the rectangle
                        self.report({'ERROR'}, f"Rectangle {r[2]} is too large for the container. Packing process cancelled.")
                        return {'CANCELLED'}


            # Start packing
            p.pack()

             # Draw the bin plane with offset
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=((container_width / 200) + bin_offset, container_height / 200, 0))
            bpy.context.object.scale.x = container_width / 100
            bpy.context.object.scale.y = container_height / 100
            plane_collection.objects.link(bpy.context.object)
            bpy.context.collection.objects.unlink(bpy.context.object)

            packed_rectangles_by_bin[bin_index] = []

            # pdb.set_trace()
            # Process packed rectangles and place them as planes with offset
            for abin in p:
                for rect in abin:
                    x, y, w, h = rect.x, rect.y, rect.width, rect.height
                    rid = rect.rid
                    original_w = w - spacing
                    original_h = h - spacing
                    scaled_w = original_w / 100
                    scaled_h = original_h / 100
                    scaled_x = (x / 100) + bin_offset
                    scaled_y = y / 100
                    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(scaled_x + scaled_w / 2, scaled_y + scaled_h / 2, 0))
                    bpy.context.object.scale.x = scaled_w
                    bpy.context.object.scale.y = scaled_h
                    plane_collection.objects.link(bpy.context.object)
                    bpy.context.collection.objects.unlink(bpy.context.object)

                    packed_rectangles_by_bin[bin_index].append((x, y, w, h, rid))

            bin_index += 1
            for rect in p.rect_list():
                # packed_rectangles.add((rect[3], rect[4]))
                packed_rectangles.add(rect[5])

          
            bin_offset += (container_width / 100) + extra_space

            # pdb.set_trace()
            packed_rectangles_data = bpy.data.collections.new("Packed Rectangles Data")
            bpy.context.scene.collection.children.link(packed_rectangles_data)

            for abin in p:
                for rect in abin:
                    x, y, w, h, rid = rect.x, rect.y, rect.width, rect.height, rect.rid
                    
                    # Corrected: Create a new empty object and set its properties
                    rect_data = bpy.data.objects.new(name=f"Rect_{rid}", object_data=None)
                    rect_data.location = (x, y, 0)  # Assuming z is 0 for a 2D plane
                    rect_data.scale = (w, h, 1)     # Assuming uniform scale in z-axis

                    # Add custom properties
                    rect_data["x"] = x
                    rect_data["y"] = y
                    rect_data["w"] = w
                    rect_data["h"] = h
                    rect_data["rid"] = rid

                    # Link the empty object to the collection
                    packed_rectangles_data.objects.link(rect_data)

            # Store the name of the collection in the scene for later retrieval
            context.scene["packed_rectangles_collection"] = packed_rectangles_data.name
            context.scene["packed_rectangles_by_bin"] = str(packed_rectangles_by_bin)


        return {'FINISHED'}


class ExportCanvasAsPDFOperator(bpy.types.Operator):
    bl_idname = "object.export_canvas_as_pdf"
    bl_label = "Export Canvas as PDF"
    bl_description = "Export the packed canvas layout as a PDF"

    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH",
        name="Save As",
        description="Save canvas layout to PDF",
        default="//canvas_layout.pdf"
    )

    def execute(self, context):
        # Retrieve the packed rectangle data from the scene
        collection_name = context.scene.get("packed_rectangles_collection", "")
        packed_rectangles_by_bin_str = context.scene.get("packed_rectangles_by_bin", "")

        if not packed_rectangles_by_bin_str:
            self.report({'ERROR'}, "Packed rectangle data not found.")
            return {'CANCELLED'}

        # Parse the string to reconstruct the dictionary
        try:
            packed_rectangles_by_bin = eval(packed_rectangles_by_bin_str)
        except:
            self.report({'ERROR'}, "Error parsing packed rectangles data.")
            return {'CANCELLED'}

        # A4 dimensions in mm
        a4_width, a4_height = 210, 297

        # Create an FPDF object with A4 dimensions
        pdf = FPDF(unit="mm", format="A4")
        # Get the canvas dimensions
        canvas_width = context.scene.container_width
        canvas_height = context.scene.container_height

        # A4 dimensions in mm (with a 5-10% margin)
        margin_percentage = 0.1  # 10% margin; adjust as needed
        effective_a4_width = a4_width * (1 - margin_percentage)
        effective_a4_height = a4_height * (1 - margin_percentage)

        # Calculate the scale factor to fit the canvas onto the A4 page
        # scale_factor = min(a4_width / canvas_width, a4_height / canvas_height)
        scale_factor = min(effective_a4_width / canvas_width, effective_a4_height / canvas_height)

        # Set font for the indices
        pdf.set_font("Arial", size=8)

        # Iterate over each bin and its rectangles
        for bin_index, rectangles in packed_rectangles_by_bin.items():
            pdf.add_page()  # Start a new page for each bin

            # Use rectangle data to draw rectangles and indices on this bin's page
            for rect in rectangles:
                x, y, w, h, rid = rect

                # Adjust for horizontal mirroring
                # Mirroring along horizontal axis by adjusting 'x'
                # adjusted_x = canvas_width - x - w
                adjusted_y = canvas_height - y - h

                # pdf_x, pdf_y, pdf_w, pdf_h = x * scale_factor, y * scale_factor, w * scale_factor, h * scale_factor

                # Scale the coordinates for the PDF
                # pdf_x, pdf_y, pdf_w, pdf_h = adjusted_x * scale_factor, y * scale_factor, w * scale_factor, h * scale_factor
                pdf_x, pdf_y, pdf_w, pdf_h = x * scale_factor, adjusted_y * scale_factor, w * scale_factor, h * scale_factor


                # Now draw the rectangle and place the index
                pdf.rect(pdf_x, pdf_y, pdf_w, pdf_h)
                
                # Calculate the center position for the index text
                index_x = pdf_x + (pdf_w / 2) - (pdf.get_string_width(str(rid)) / 2)
                index_y = pdf_y + (pdf_h / 2) + 2  # Adjusted for text height

                pdf.set_xy(index_x, index_y)
                pdf.cell(pdf.get_string_width(str(rid)), 0, str(rid), 0, 0, 'C')  # Center align the index

        # Save the PDF to the specified filepath
        pdf.output(self.filepath)

        self.report({'INFO'}, f"Canvas layout exported as PDF to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}




# Ovaj dio projektuje geometriju linearno u strip
class RunProjectObjectsOperator(bpy.types.Operator):
    bl_idname = "object.run_project_objects"
    bl_label = "Strip"

    def execute(self, context):
        rectangles = []
        next_x, next_y = 0, 0  # Initialize start positions
        # spacing = 0.5
        spacing = context.scene.spacing / 100 # uniti su po defaultu u metrima

        # Use dimension_entries for the dimensions
        for entry in context.scene.dimension_entries:
            sorted_dims = sorted([entry.width, entry.height, entry.length])
            rectangles.append((int(sorted_dims[1]), int(sorted_dims[2])))

        # Sort rectangles by one dimension for better tiling
        rectangles.sort(key=lambda x: x[0])

        # Tile the planes on the ground
        for w, h in rectangles:
            # First create a plane at the origin
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(0, 0, 0))
            # Then scale it
            bpy.context.object.scale[0] = w / 100
            bpy.context.object.scale[1] = h / 100
            # Then translate it to the correct position
            bpy.context.object.location.x = next_x + (w / 2) / 100
            bpy.context.object.location.y = next_y + (h / 2) / 100

            # Update the next start position (convert w from Blender units to your units)
            next_x += (w / 100) + spacing

            # Optional: you can add some "spacing" between each tile if you like
            # next_x += (w / 100) + 0.05  # 0.05 units of spacing

        return {'FINISHED'}



def register():
    bpy.utils.register_class(PackedRectangle)
    bpy.utils.register_class(RunNestingAlgorithmOperator)
    bpy.utils.register_class(RunProjectObjectsOperator)
    bpy.utils.register_class(ExportCanvasAsPDFOperator)

def unregister():
    bpy.utils.unregister_class(PackedRectangle)
    bpy.utils.unregister_class(RunNestingAlgorithmOperator)
    bpy.utils.unregister_class(RunProjectObjectsOperator)
    bpy.utils.unregister_class(ExportCanvasAsPDFOperator)

if __name__ == "__main__":
    register()
