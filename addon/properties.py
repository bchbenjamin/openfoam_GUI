import bpy

class ClassyMeshObjectProperties(bpy.types.PropertyGroup):
    exclude_from_mesh: bpy.props.BoolProperty(
        name="Exclude from Mesh",
        default=False,
        description="Exclude this object from the blockMeshDict generation"
    )
    cells: bpy.props.IntVectorProperty(name="Cells X/Y/Z", default=(10, 10, 10), min=1)
    patch_name: bpy.props.StringProperty(name="Patch Name", default="defaultWall")

    # --- Block type ---
    block_type: bpy.props.EnumProperty(
        name="Block Type",
        description="How this object maps to a classy_blocks block",
        items=[
            ("BOX",     "Box",     "Axis-aligned rectangular block (uses bounding box)"),
            ("EXTRUDE", "Extrude", "Extrude a quad face along a vector"),
            ("REVOLVE", "Revolve", "Revolve a quad face around an axis"),
        ],
        default="BOX",
    )

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

    # --- STL Projection properties (BOX only, e.g. terrain) ---
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

    # --- EXTRUDE parameters ---
    extrude_face_index: bpy.props.IntProperty(
        name="Face Index",
        description="Index of the quad face to extrude (from Edit Mode)",
        default=0, min=0,
    )
    extrude_axis: bpy.props.EnumProperty(
        name="Extrude Along",
        items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")],
        default="Z",
    )
    extrude_distance: bpy.props.FloatProperty(
        name="Extrude Distance (m)",
        default=1.0,
    )

    # --- REVOLVE parameters ---
    revolve_face_index: bpy.props.IntProperty(
        name="Face Index", default=0, min=0,
    )
    revolve_angle: bpy.props.FloatProperty(
        name="Angle (degrees)", default=90.0, min=-360.0, max=360.0,
    )
    revolve_axis: bpy.props.EnumProperty(
        name="Revolution Axis",
        items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")],
        default="Z",
    )
    revolve_origin: bpy.props.FloatVectorProperty(
        name="Axis Origin", default=(0.0, 0.0, 0.0), size=3,
    )


class ClassyMeshSceneProperties(bpy.types.PropertyGroup):
    case_path: bpy.props.StringProperty(
        name="Case Directory", 
        default="",
        subtype='DIR_PATH',
        description="Path to the OpenFOAM case directory. "
                    "Will be created automatically if it doesn't exist."
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
    structure_warning: bpy.props.StringProperty(
        name="Structure Warning",
        default=""
    )
    last_generated_has_disk: bpy.props.BoolProperty(
        name="Last Generated Has Disk",
        default=False
    )
    last_mesh_quality: bpy.props.StringProperty(
        name="Last Quality",
        default=""
    )
    last_mesh_quality_icon: bpy.props.StringProperty(
        name="Last Quality Icon",
        default="INFO"
    )
