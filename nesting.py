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

   
        # # Retrieve rectangle dimensions
        # rectangles = []
        # for entry in context.scene.dimension_entries:
        #     sorted_dims = sorted([entry.width, entry.height, entry.length])
        #     rectangles.append((int(sorted_dims[1]), int(sorted_dims[2])))


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

            # pdb.set_trace()
             # Draw the bin plane with offset
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=((container_width / 200) + bin_offset, container_height / 200, 0))
            bpy.context.object.scale.x = container_width / 100
            bpy.context.object.scale.y = container_height / 100
            plane_collection.objects.link(bpy.context.object)
            bpy.context.collection.objects.unlink(bpy.context.object)

               # Process packed rectangles and place them as planes with offset
            for abin in p:
                for rect in abin:
                    x, y, w, h = rect.x, rect.y, rect.width, rect.height
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

            # pdb.set_trace()
            for rect in p.rect_list():
                # packed_rectangles.add((rect[3], rect[4]))
                packed_rectangles.add(rect[5])

          
            bin_offset += (container_width / 100) + extra_space

        return {'FINISHED'}



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
        pdb.set_trace()
        # A4 dimensions in mm
        a4_width, a4_height = 210, 297

        # Create an FPDF object with A4 dimensions
        pdf = FPDF(unit="mm", format="A4")
        pdf.add_page()

        # Get the canvas dimensions (assuming they are stored in the scene properties)
        canvas_width = context.scene.container_width
        canvas_height = context.scene.container_height

        # Calculate the scale factor to fit the canvas onto the A4 page
        scale_factor = min(a4_width / canvas_width, a4_height / canvas_height)

        # Draw the rectangles on the PDF
        for entry in context.scene.dimension_entries:
            # Get rectangle dimensions and position
            # Assuming the positions are stored in the entry
            rect_x, rect_y, rect_w, rect_h = entry.x, entry.y, entry.width, entry.height

            # Scale and position the rectangle on the PDF
            pdf_x = rect_x * scale_factor
            pdf_y = rect_y * scale_factor
            pdf_w = rect_w * scale_factor
            pdf_h = rect_h * scale_factor

            # Draw the rectangle on the PDF
            pdf.rect(pdf_x, pdf_y, pdf_w, pdf_h)

        # Save the PDF to the specified filepath
        pdf.output(self.filepath)

        self.report({'INFO'}, f"Canvas layout exported as PDF to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(RunNestingAlgorithmOperator)
    bpy.utils.register_class(RunProjectObjectsOperator)
    bpy.utils.register_class(ExportCanvasAsPDFOperator)

def unregister():
    bpy.utils.unregister_class(RunNestingAlgorithmOperator)
    bpy.utils.unregister_class(RunProjectObjectsOperator)
    bpy.utils.unregister_class(ExportCanvasAsPDFOperator)

if __name__ == "__main__":
    register()
