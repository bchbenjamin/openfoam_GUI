import bpy

class ClassyMeshObjectProperties(bpy.types.PropertyGroup):
    exclude_from_mesh: bpy.props.BoolProperty(
        name="Exclude from Mesh",
        default=False,
        description="Exclude this object from the blockMeshDict generation"
    )
    force_include: bpy.props.BoolProperty(
        name="Force Include",
        default=False,
        description="Include this object even if it's detected as 2D/unsupported"
    )
    cells: bpy.props.IntVectorProperty(name="Cells X/Y/Z", default=(10, 10, 10), min=1)
    patch_name: bpy.props.StringProperty(name="Patch Name", default="defaultWall")

    # --- Block type ---
    block_type: bpy.props.EnumProperty(
        name="Block Type",
        description="How this object maps to a classy_blocks block",
        items=[
            ("BOX",           "Box",           "Axis-aligned rectangular block"),
            ("CYLINDER",      "Cylinder",      "Standard cylindrical pipe"),
            ("FRUSTUM",       "Frustum",       "Tapered cone or frustum"),
            ("EXTRUDED_RING", "Extruded Ring", "Cylinder with a central hole (pipe wall)"),
            ("WEDGE",         "Wedge",         "Axisymmetric 2D slice"),
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
    stl_file: bpy.props.StringProperty(name="STL File", subtype="FILE_PATH", default="")

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

    # --- LOFT parameters ---
    loft_bottom_face_index: bpy.props.IntProperty(
        name="Bottom Face Index",
        description="Index of the bottom quad face (from Edit Mode)",
        default=0, min=0,
    )
    loft_top_face_index: bpy.props.IntProperty(
        name="Top Face Index",
        description="Index of the top quad face (from Edit Mode)",
        default=1, min=0,
    )

    # --- WEDGE parameters ---
    wedge_face_index: bpy.props.IntProperty(
        name="Face Index",
        description="Index of the quad face to create wedge from (from Edit Mode)",
        default=0, min=0,
    )
    wedge_angle: bpy.props.FloatProperty(
        name="Wedge Angle (degrees)",
        description="Total wedge angle — use 2 to 5 degrees for axisymmetric CFD",
        default=2.0, min=0.1, max=30.0,
    )

    # --- Shape Chaining parameters ---
    chain_source: bpy.props.StringProperty(
        name="Chain From",
        description="Name of the source object to chain this shape from",
        default="",
    )
    chain_length: bpy.props.FloatProperty(
        name="Chain Length (m)",
        description="Length of the chained pipe segment",
        default=1.0, min=0.001,
    )
    chain_radius_2: bpy.props.FloatProperty(
        name="End Radius (m)",
        description="End radius for frustum chains (0 = same as source)",
        default=0.0, min=0.0,
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
        default=False,
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

    last_mesh_quality: bpy.props.StringProperty(
        name="Last Quality",
        default=""
    )
    last_mesh_quality_icon: bpy.props.StringProperty(
        name="Last Quality Icon",
        default="INFO"
    )
