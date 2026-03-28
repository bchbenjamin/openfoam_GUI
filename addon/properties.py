import bpy

class ClassyMeshObjectProperties(bpy.types.PropertyGroup):
    is_block: bpy.props.BoolProperty(name="Is Mesh Block", default=False)
    block_type: bpy.props.EnumProperty(
        name="Block Type",
        items=[("box", "Box", ""), ("extrude", "Extrude", ""), ("revolve", "Revolve", "")]
    )
    cells: bpy.props.IntVectorProperty(name="Cells X/Y/Z", default=(10, 10, 10), min=1)
    patch_name: bpy.props.StringProperty(name="Patch Name", default="defaultWall")

    # --- Grading properties (Week 5) ---
    grading_type: bpy.props.EnumProperty(
        name="Grading Type",
        items=[
            ("RATIO", "C2C Ratio", "Cell-to-cell expansion ratio (uniform if 1.0)"),
            ("START_SIZE", "Start Size", "Specify first cell size in meters"),
            ("SYMMETRIC", "Symmetric", "Specify first and last cell sizes"),
        ],
        default="RATIO",
    )
    grading: bpy.props.FloatVectorProperty(
        name="Grading (C2C)", size=3,
        default=(1.0, 1.0, 1.0), min=0.01, max=100.0,
    )
    start_size: bpy.props.FloatProperty(
        name="First Cell Size (m)",
        default=1e-4, min=1e-10, precision=8,
    )
    end_size: bpy.props.FloatProperty(
        name="Last Cell Size (m)",
        default=1e-4, min=1e-10, precision=8,
    )

    # --- STL Projection properties (Week 5) ---
    stl_projection_face: bpy.props.EnumProperty(
        name="Project Face",
        items=[
            ("top", "Top", ""),
            ("bottom", "Bottom", ""),
            ("front", "Front", ""),
            ("back", "Back", ""),
            ("left", "Left", ""),
            ("right", "Right", ""),
        ],
    )
    stl_file: bpy.props.StringProperty(name="STL File", subtype="FILE_PATH")


class ClassyMeshSceneProperties(bpy.types.PropertyGroup):
    case_path: bpy.props.StringProperty(name="Case Directory", subtype='DIR_PATH')
    bashrc_path: bpy.props.StringProperty(name="OpenFOAM bashrc", default="/opt/openfoam13/etc/bashrc", subtype='FILE_PATH')

    # --- Auto-Update Mesh properties (Week 5) ---
    use_auto_update: bpy.props.BoolProperty(
        name="Auto-Update Mesh",
        default=True,
        description="Automatically mesh and reload on change if small project",
    )
    auto_update_limit: bpy.props.IntProperty(
        name="Update Block Limit",
        default=50,
        description="Disable auto-update if block/cell threshold passed",
    )
    auto_update_delay: bpy.props.FloatProperty(
        name="Update Delay (s)",
        default=2.0, min=0.5, max=10.0,
    )
