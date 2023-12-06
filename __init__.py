bl_info = {
        "name": "Arka",
        "description": "Plugin for bin packing",
        "author": "Noah",
        "version": (1, 0),
        "blender": (3, 6, 4),   
        "location": "Properties > Render > My Awesome Panel",
        "warning": "", # used for warning icon and text in add-ons panel
#         Ovdje ces da stavis link ka dokumentaciji
        "wiki_url": "http://my.wiki.url",
        "tracker_url": "https://developer.blender.org/maniphest/task/edit/form/2/",
        # "tracker_url": "http://my.bugtracker.url",
        "support": "COMMUNITY",
        "category": "Organization"
        }

from . import operators
# from . import supabaseOperators
from . import ui
from . import properties
from . import nesting

def register():
    operators.register()
    # supabaseOperators.register()
    ui.register()
    properties.register()
    nesting.register()

def unregister():
    operators.unregister()
    # supabaseOperators.unregister()
    ui.unregister()
    properties.unregister()
    nesting.unregister()

if __name__ == "__main__":
    register()
