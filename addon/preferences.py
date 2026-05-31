import bpy

class ClassyBlocksPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    bashrc_path: bpy.props.StringProperty(
        name="OpenFOAM bashrc",
        default="/opt/openfoam13/etc/bashrc",
        subtype='FILE_PATH'
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
        layout.prop(self, "merge_tolerance")
        
        layout.separator()
        layout.label(text="Auto-Update Mesh Thresholds")
        layout.prop(self, "auto_update_limit")
        layout.prop(self, "auto_update_delay")
