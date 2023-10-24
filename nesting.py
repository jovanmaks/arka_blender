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
                if all(_no_overlap(x, y, w, h, p) for p in packed):
                    packed.append(Rectangle(x, y, w, h))
                    found_spot = True
                    break
            if found_spot:
                break
    return packed

# Check for overlapping rectangles
def _no_overlap(x1, y1, w1, h1, rect2):
    x2, y2, w2, h2 = rect2
    return x1 >= x2 + w2 or x1 + w1 <= x2 or y1 >= y2 + h2 or y1 + h1 <= y2

class RunNestingAlgorithmOperator(bpy.types.Operator):
    bl_idname = "object.run_nesting_algorithm"
    bl_label = "Run Nesting Algorithm"

    def execute(self, context):
        container_width = context.scene.container_width
        container_height = context.scene.container_height
        rectangles = []

        for entry in context.scene.dimension_entries:
            sorted_dims = sorted([entry.width, entry.height, entry.length])
            rectangles.append((int(sorted_dims[0]), int(sorted_dims[1])))

        result = _greedy_nest_rectangles(container_width, container_height, rectangles)

        for x, y, w, h in result:
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(x + w / 2, y + h / 2, 0))
            bpy.context.object.scale[0] = w / 2
            bpy.context.object.scale[1] = h / 2

        return {'FINISHED'}

def register():
    bpy.utils.register_class(RunNestingAlgorithmOperator)

def unregister():
    bpy.utils.unregister_class(RunNestingAlgorithmOperator)

if __name__ == "__main__":
    register()

