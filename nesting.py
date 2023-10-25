import bpy
from collections import namedtuple
import pdb

# NamedTuple to represent a rectangle
Rectangle = namedtuple("Rectangle", ["x", "y", "w", "h"])

# FreeRect to represent a free area in the container
Rect = namedtuple("Rect", ["x", "y", "w", "h"])

def guillotine_bin_packing(container_width, container_height, rectangles):
    packed = []
    free_rects = [Rect(0, 0, container_width, container_height)]
    new_free_rects = []

    for w, h in rectangles:
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

        new_free_rects.append(Rect(best_rect.x + w, best_y, best_rect.w - w, h))
        new_free_rects.append(Rect(best_x, best_rect.y + h, w, best_rect.h - h))

        free_rects = [rect for rect in free_rects if not (rect.x >= best_x and rect.y >= best_y and rect.x + rect.w <= best_x + w and rect.y + rect.h <= best_y + h)]
        free_rects.extend(new_free_rects)
        new_free_rects.clear()

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
        container_width = context.scene.container_width
        container_height = context.scene.container_height
        rectangles = []

        # scale_factor = 1/10   # adjust this as needed

        for entry in context.scene.dimension_entries:
            sorted_dims = sorted([entry.width, entry.height, entry.length])
            # scaled_w = int(sorted_dims[1] * scale_factor)
            # scaled_h = int(sorted_dims[2] * scale_factor)
            # rectangles.append((scaled_w, scaled_h))
            rectangles.append((int(sorted_dims[1]), int(sorted_dims[2])))

        pdb.set_trace()
        result = guillotine_bin_packing(container_width, container_height, rectangles)
        pdb.set_trace()

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


