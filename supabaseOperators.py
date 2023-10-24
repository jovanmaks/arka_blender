import bpy
from supabase import create_client, Client

# Initialize the Supabase client
SUPABASE_URL = "https://hvxevciwsckvrcvbldek.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2eGV2Y2l3c2NrdnJjdmJsZGVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTY2NjIzNDYsImV4cCI6MjAxMjIzODM0Nn0.iEs84FRr90owSSjMTBZtNUJl6aGr43sE-aU2v9v6cWA"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseLoginPanel(bpy.types.Panel):
    bl_label = "Database Login"
    bl_idname = "PT_SupabaseLoginPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'
    
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "email", text="Email")
        
        row = layout.row()
        row.prop(context.scene, "password", text="Password")
        
        row = layout.row()
        row.operator("object.supabase_login", text="Login")

class SupabaseLoginOperator(bpy.types.Operator):
    bl_idname = "object.supabase_login"
    bl_label = "Login to Supabase"

    def execute(self, context):
        email = context.scene.email
        password = context.scene.password
            
        credentials = {"email": email, "password": password}
        response = supabase.auth.sign_in_with_password(credentials)

        # print("Full Supabase response:", response)

        # if hasattr(response, 'error') and response.error:
        #     self.report({'ERROR'}, f"Authentication failed: {response.error.message}")
        #     return {'FINISHED'}

        # user = getattr(response, 'user', None)
        # print("User Object:", user)
        # print("User Object Attributes:", dir(user))  # This will print all attributes of the user object

        # if not user or not hasattr(user, 'access_token'):
        #     self.report({'ERROR'}, "Failed to find access token in user object")
        #     return {'FINISHED'}

        response = supabase.table('user_relationship').select("*").execute()

        if response.data:
            # Print the ID of the fetched row
            print(response.data[0]['id'])  # Assuming you have a column named 'id'
            self.report({'INFO'}, "Fetched ID: " + str(response.data[0]['id']))
        else:
            self.report({'ERROR'}, "Failed to fetch data from user_relationship table.")


        return {'FINISHED'}


def register():
    bpy.types.Scene.email = bpy.props.StringProperty(name="Email", default="")
    bpy.types.Scene.password = bpy.props.StringProperty(name="Password", subtype='PASSWORD')
    bpy.utils.register_class(SupabaseLoginPanel)
    bpy.utils.register_class(SupabaseLoginOperator)


def unregister():
    bpy.utils.unregister_class(SupabaseLoginPanel)
    bpy.utils.unregister_class(SupabaseLoginOperator)
    del bpy.types.Scene.email
    del bpy.types.Scene.password