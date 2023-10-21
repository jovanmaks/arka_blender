bl_info = {
        "name": "Arka",
        "description": "Plugin for managing plates",
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
from . import ui
from . import properties

def register():
    operators.register()
    ui.register()
    properties.register()

def unregister():
    operators.unregister()
    ui.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()
