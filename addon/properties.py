import bpy

class ClassyMeshObjectProperties(bpy.types.PropertyGroup):
    is_block: bpy.props.BoolProperty(name="Is Mesh Block", default=False)
    block_type: bpy.props.EnumProperty(
        name="Block Type",
        items=[("box", "Box", ""), ("extrude", "Extrude", ""), ("revolve", "Revolve", "")]
    )
    cells: bpy.props.IntVectorProperty(name="Cells X/Y/Z", default=(10, 10, 10), min=1)
    patch_name: bpy.props.StringProperty(name="Patch Name", default="defaultWall")

    # --- Grading properties ---
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

    # --- STL Projection properties ---
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
    case_path: bpy.props.StringProperty(
        name="Case Directory", 
        default="~/foam_cases/default_case/",
        subtype='DIR_PATH'
    )

    # --- Auto-Update Mesh properties ---
    use_auto_update: bpy.props.BoolProperty(
        name="Auto-Update Mesh",
        default=True,
        description="Automatically mesh and reload on change if small project",
    )

    # --- Status properties ---
    pipeline_status: bpy.props.StringProperty(
        name="Status",
        default="Ready"
    )
    last_mesh_quality: bpy.props.StringProperty(
        name="Last Quality",
        default=""
    )
    last_mesh_quality_icon: bpy.props.StringProperty(
        name="Last Quality Icon",
        default="INFO"
    )
