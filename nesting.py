import bpy
from collections import namedtuple
import pdb
from .rectpack import newPacker

# NamedTuple to represent a rectangle
Rectangle = namedtuple("Rectangle", ["x", "y", "w", "h"])

# FreeRect to represent a free area in the container
Rect = namedtuple("Rect", ["x", "y", "w", "h"])

def maximal_rectangles_bin_packing(container_width, container_height, rectangles, spacing=0):
    packed = []
    free_rects = [Rect(0, 0, container_width, container_height)]

    def can_place_rect(free_rect, rect_w, rect_h):
        return free_rect.w >= rect_w and free_rect.h >= rect_h

    for rect_w, rect_h in rectangles:
        rect_w_with_spacing = rect_w + spacing
        rect_h_with_spacing = rect_h + spacing

        best_score = float('inf')
        best_rect = None

        for free_rect in free_rects:
            if can_place_rect(free_rect, rect_w, rect_h):
                score = free_rect.w * free_rect.h
                if score < best_score:
                    best_score = score
                    best_rect = free_rect

        if best_rect is None:
            continue

        packed_rect = Rect(best_rect.x, best_rect.y, rect_w, rect_h)
        packed.append(packed_rect)

        new_free_rects = []
        for free_rect in free_rects:
            new_rects = [
                Rect(free_rect.x, best_rect.y + rect_h_with_spacing, free_rect.w, free_rect.h - (best_rect.y + rect_h_with_spacing - free_rect.y)),
                Rect(best_rect.x + rect_w_with_spacing, free_rect.y, free_rect.w - (best_rect.x + rect_w_with_spacing - free_rect.x), free_rect.h)
            ]

            for new_rect in new_rects:
                if new_rect.w > 0 and new_rect.h > 0:
                    new_free_rects.append(new_rect)

        free_rects = new_free_rects

    return packed



def guillotine_bin_packing(container_width, container_height, rectangles, spacing=0):
    packed = []
    free_rects = [Rect(0, 0, container_width, container_height)]
    
    def is_overlapping(r1, r2):
        return not (r1.x + r1.w <= r2.x or r1.x >= r2.x + r2.w or r1.y + r1.h <= r2.y or r1.y >= r2.y + r2.h)

    # pdb.set_trace()
    for w, h in rectangles:
        w_with_spacing = w + spacing
        h_with_spacing = h + spacing

        best_rect_idx, best_x, best_y, best_area = -1, None, None, None

        for i, rect in enumerate(free_rects):
            if rect.w >= w and rect.h >= h:
                area = rect.w * rect.h
                if best_area is None or area < best_area:
                    best_area = area
                    best_x, best_y = rect.x, rect.y
                    best_rect_idx = i

        if best_rect_idx == -1:
            continue

        packed.append(Rect(best_x, best_y, w, h))
        best_rect = free_rects.pop(best_rect_idx)

        new_free_rect1 = Rect(best_rect.x + w_with_spacing, best_y, best_rect.w - w_with_spacing, h)
        new_free_rect2 = Rect(best_x, best_rect.y + h_with_spacing, w, best_rect.h - h_with_spacing)


        # Check if new free rectangles overlap with existing ones
        for r in free_rects:
            if is_overlapping(new_free_rect1, r):
                new_free_rect1 = None
            if is_overlapping(new_free_rect2, r):
                new_free_rect2 = None

        if new_free_rect1:
            free_rects.append(new_free_rect1)
        if new_free_rect2:
            free_rects.append(new_free_rect2)

    return packed

# Check for overlapping rectangles and also if it goes out of the container
def _no_overlap(x1, y1, w1, h1, rect2, container_width, container_height):
    x2, y2, w2, h2 = rect2
    no_overlap = x1 >= x2 + w2 or x1 + w1 <= x2 or y1 >= y2 + h2 or y1 + h1 <= y2
    within_bounds = x1 + w1 <= container_width and y1 + h1 <= container_height
    return no_overlap and within_bounds




class RunNestingAlgorithmOperator(bpy.types.Operator):
    bl_idname = "object.run_nesting_algorithm"
    bl_label = "Max rect with rectpack"

    def execute(self, context):
        container_width = context.scene.container_width
        container_height = context.scene.container_height
        spacing = context.scene.spacing     

        # # Retrieve rectangle dimensions
        # rectangles = []
        # for entry in context.scene.dimension_entries:
        #     sorted_dims = sorted([entry.width, entry.height, entry.length])
        #     rectangles.append((int(sorted_dims[1]), int(sorted_dims[2])))

        rectangles = []
        for entry in context.scene.dimension_entries:
            sorted_dims = sorted([entry.width, entry.height, entry.length])
            rect_width_with_spacing = int(sorted_dims[1]) + spacing
            rect_height_with_spacing = int(sorted_dims[2]) + spacing
            rectangles.append((rect_width_with_spacing, rect_height_with_spacing))

        # pdb.set_trace()
        # Initialize packer and add rectangles and bins
        packer = newPacker()
        for r in rectangles:
            packer.add_rect(*r)
        packer.add_bin(container_width, container_height)

        # Start packing
        packer.pack()

        # Create a new collection for the planes
        plane_collection = bpy.data.collections.new("Packed Planes")
        bpy.context.scene.collection.children.link(plane_collection)
        
        # This is the big plane
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(container_width / 200, container_height / 200, 0))
        bpy.context.object.scale.x = container_width / 100
        bpy.context.object.scale.y = container_height / 100

        # pdb.set_trace()
       # Process packed rectangles and place them as planes without spacing
        for abin in packer:
            for rect in abin:
                x, y, w, h = rect.x, rect.y, rect.width, rect.height

                # Subtract spacing to get original dimensions for drawing
                original_w = w - spacing
                original_h = h - spacing

                # Scale the dimensions for drawing
                scaled_w = original_w / 100
                scaled_h = original_h / 100

                # Calculate the scaled position
                scaled_x = (x / 100) 
                scaled_y = (y / 100)

                # Create the plane at the scaled position
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(scaled_x + scaled_w / 2, scaled_y + scaled_h / 2, 0))
                bpy.context.object.scale.x = scaled_w
                bpy.context.object.scale.y = scaled_h

                # Link the object to the new collection
                plane_collection.objects.link(bpy.context.object)
                bpy.context.collection.objects.unlink(bpy.context.object)

        return {'FINISHED'}


class RunGuillotineAlgorithmOperator(bpy.types.Operator):
    bl_idname = "object.run_guillotine_algorithm"
    bl_label = "Guillotine"

    def execute(self, context):
        container_width = context.scene.container_width
        container_height = context.scene.container_height
        spacing = context.scene.spacing
        rectangles = []

        # scale_factor = 1/10   # adjust this as needed

        for entry in context.scene.dimension_entries:
            sorted_dims = sorted([entry.width, entry.height, entry.length])
            rectangles.append((int(sorted_dims[1]), int(sorted_dims[2])))

        # pdb.set_trace()
        result = guillotine_bin_packing(container_width, container_height, rectangles,spacing)
        # pdb.set_trace()

        scale_factor = 0.01  # Adjust this as needed
        # Create a new collection for the planes
        plane_collection = bpy.data.collections.new("Packed Planes")
        bpy.context.scene.collection.children.link(plane_collection)

        for x, y, w, h in result:
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(x + w / 2, y + h / 2, 0))
            bpy.context.object.scale.x = w
            bpy.context.object.scale.y = h

            # Link the object to the new collection
            plane_collection.objects.link(bpy.context.object)
            bpy.context.collection.objects.unlink(bpy.context.object)

        # Set 3D cursor to a base point, let's say (0, 0, 0)
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

        # Set the pivot point to the 3D cursor
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'

        # Select all objects in the collection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in plane_collection.objects:
            obj.select_set(True)

        # Scale them together
        scale_factor = 0.01  # Replace this with the scale factor you want
        bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))

        # Reset the pivot point if necessary
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

        # This is the big plane
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(container_width / 200, container_height / 200, 0))
        bpy.context.object.scale.x = container_width / 100
        bpy.context.object.scale.y = container_height / 100
        

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





def register():
    bpy.utils.register_class(RunNestingAlgorithmOperator)
    bpy.utils.register_class(RunGuillotineAlgorithmOperator)
    bpy.utils.register_class(RunProjectObjectsOperator)

def unregister():
    bpy.utils.unregister_class(RunNestingAlgorithmOperator)
    bpy.utils.unregister_class(RunGuillotineAlgorithmOperator)
    bpy.utils.unregister_class(RunProjectObjectsOperator)

if __name__ == "__main__":
    register()


