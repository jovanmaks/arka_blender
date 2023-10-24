import bpy
from collections import namedtuple

# NamedTuple to represent a rectangle
Rectangle = namedtuple("Rectangle", ["x", "y", "w", "h"])

# Greedy algorithm for nesting rectangles
def _greedy_nest_rectangles(container_width, container_height, rectangles):
    packed = []
    for rect in rectangles:
        w, h = rect
        found_spot = False
        for x in range(0, container_width - w + 1):
            for y in range(0, container_height - h + 1):
                if all(_no_overlap(x, y, w, h, p, container_width, container_height) for p in packed):
                    print(f"Placing rectangle at {x},{y} of size {w}x{h}")
                    packed.append(Rectangle(x, y, w, h))
                    found_spot = True
                    break
            if found_spot:
                break
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

        for entry in context.scene.dimension_entries:
            sorted_dims = sorted([entry.width, entry.height, entry.length])
            rectangles.append((int(sorted_dims[1]), int(sorted_dims[2])))

        result = _greedy_nest_rectangles(container_width, container_height, rectangles)

        for x, y, w, h in result:
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(x + w / 2, y + h / 2, 0))
            bpy.context.object.scale[0] = w/100  # Removed the division by 2
            bpy.context.object.scale[1] = h/100  # Removed the division by 2

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


