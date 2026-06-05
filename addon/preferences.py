import bpy
import os

def get_default_bashrc():
    # Check if there is a local OpenFOAM-13 symlink/directory inside the addon
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    for name in ["OpenFOAM-13", "openfoam13"]:
        local_bashrc = os.path.join(addon_dir, name, "etc", "bashrc")
        if os.path.exists(local_bashrc):
            return local_bashrc
    
    # Fallback to system /opt path
    return "/opt/openfoam13/etc/bashrc"

class ClassyBlocksPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    bashrc_path: bpy.props.StringProperty(
        name="OpenFOAM bashrc",
        default=get_default_bashrc(),
        subtype='FILE_PATH'
    )
    default_case_dir: bpy.props.StringProperty(
        name="Default Case Directory",
        default="",
        subtype='DIR_PATH',
        description="Global fallback case directory"
    )
    merge_tolerance: bpy.props.FloatProperty(
        name="Merge Tolerance",
        default=1e-4,
        min=1e-6,
        precision=6,
        description="Vertices closer than this are merged by blockMesh"
    )
    auto_update_limit: bpy.props.IntProperty(
        name="Auto-Update Block Limit",
        default=50,
        description="Disable auto-update if block/cell threshold passed"
    )
    auto_update_delay: bpy.props.FloatProperty(
        name="Auto-Update Delay (s)",
        default=2.0, min=0.5, max=10.0,
        description="Wait time before auto-running meshing pipeline"
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="System Settings")
        layout.prop(self, "bashrc_path")
        layout.prop(self, "default_case_dir")
        layout.prop(self, "merge_tolerance")
        
        layout.separator()
        layout.label(text="Auto-Update Mesh Thresholds")
        layout.prop(self, "auto_update_limit")
        layout.prop(self, "auto_update_delay")
