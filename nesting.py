
import bpy


# Greedy nesting
def greedy_nest_squares(container_width, container_height, squares):
    squares = sorted(squares, reverse=True)  # Sort squares by side length
    used_space = []  # To store positions of placed squares
    for square in squares:
        placed = False
        for x in range(container_width - square + 1):
            for y in range(container_height - square + 1):
                if all((x2 > x + square or x2 + s <= x or y2 > y + square or y2 + s <= y)
                        for x2, y2, s in used_space):
                    used_space.append((x, y, square))
                    placed = True
                    breaki
            if placed:
                break
    return used_space


class RunNestingAlgorithmOperator(bpy.types.Operator):
    bl_idname = "object.run_nesting_algorithm"
    bl_label = "Run Nesting Algorithm"

    def execute(self, context):
        container_width = context.scene.container_width
        container_height = context.scene.container_height

        # Fetch squares from dimension_entries or similar, convert to list
        squares = [...]  

        result = greedy_nest_squares(container_width, container_height, squares)
        # Do something with the result, like drawing squares in the Blender scene

        return {'FINISHED'}



def register():
    bpy.utils.register_class(RunNestingAlgorithmOperator)



def unregister():
    bpy.utils.unregister_class(RunNestingAlgorithmOperator)