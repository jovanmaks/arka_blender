import bpy
from collections import namedtuple
import pdb

# NamedTuple to represent a rectangle
Rectangle = namedtuple("Rectangle", ["x", "y", "w", "h"])

# FreeRect to represent a free area in the container
FreeRect = namedtuple("FreeRect", ["x", "y", "w", "h"])

# The Guillotine bin packing algorithm
def guillotine_bin_packing(container_width, container_height, rectangles):
    packed = []
    free_rects = [FreeRect(0, 0, container_width, container_height)]

    for w, h in rectangles:
        best_rect_idx = -1
        best_x, best_y = 0, 0
        best_area = float('inf')

        # Find the best spot for this rectangle
        for i, rect in enumerate(free_rects):
            if rect.w >= w and rect.h >= h:
                area = rect.w * rect.h
                if area < best_area:
                    best_area = area
                    best_x, best_y = rect.x, rect.y
                    best_rect_idx = i

        if best_rect_idx == -1:
            continue  # Couldn't find a spot, skipping

        # Place the rectangle
        packed.append(Rectangle(best_x, best_y, w, h))

        # Update free rectangles
        free_rect = free_rects.pop(best_rect_idx)
        free_rects.append(FreeRect(free_rect.x + w, free_rect.y, free_rect.w - w, h))
        free_rects.append(FreeRect(free_rect.x, free_rect.y + h, w, free_rect.h - h))

    return packed

# Check for overlapping rectangles and also if it goes out of the container
def _no_overlap(x1, y1, w1, h1, rect2, container_width, container_height):
    x2, y2, w2, h2 = rect2
    no_overlap = x1 >= x2 + w2 or x1 + w1 <= x2 or y1 >= y2 + h2 or y1 + h1 <= y2
    within_bounds = x1 + w1 <= container_width and y1 + h1 <= container_height
    return no_overlap and within_bounds

class RunNestingAlgorithmOperator(bpy.types.Operator):
    bl_idname = "object.run_nesting_algorithm"
    bl_label = "Pack"

    def execute(self, context):
        pdb.set_trace()
        container_width = context.scene.container_widthcon
        container_height = context.scene.container_height
        rectangles = []

        scale_factor = 1/10   # adjust this as needed

        for entry in context.scene.dimension_entries:
            sorted_dims = sorted([entry.width, entry.height, entry.length])
            print("Sorted dimensions:", sorted_dims)  # Debug line
            scaled_w = int(sorted_dims[1] * scale_factor)
            scaled_h = int(sorted_dims[2] * scale_factor)
            print("scaled_w:", scaled_w, "scaled_h:", scaled_h)  # Debug line
            rectangles.append((scaled_w, scaled_h))

        pdb.set_trace()
        result = guillotine_bin_packing(container_width, container_height, rectangles)
        pdb.set_trace()

        for x, y, w, h in result:
            pdb.set_trace()
            # Create a plane at the origin
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(0, 0, 0))
            
            # Then translate it to the correct position
            bpy.context.object.location.x = x + w / 2
            bpy.context.object.location.y = y + h / 2

            # Scale it after translation
            bpy.context.object.scale.x = w
            bpy.context.object.scale.y = h


        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(container_width / 2, container_height / 2, 0))
        bpy.context.object.scale.x = container_width
        bpy.context.object.scale.y = container_height
        

        return {'FINISHED'}


class RunProjectObjectsOperator(bpy.types.Operator):
    bl_idname = "object.run_project_objects"
    bl_label = "Project"

    def execute(self, context):
        rectangles = []
        next_x, next_y = 0, 0  # Initialize start positions

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
            next_x += w / 100

            # Optional: you can add some "spacing" between each tile if you like
            # next_x += (w / 100) + 0.05  # 0.05 units of spacing

        return {'FINISHED'}





def register():
    bpy.utils.register_class(RunNestingAlgorithmOperator)
    bpy.utils.register_class(RunProjectObjectsOperator)

def unregister():
    bpy.utils.unregister_class(RunNestingAlgorithmOperator)
    bpy.utils.unregister_class(RunProjectObjectsOperator)

if __name__ == "__main__":
    register()


