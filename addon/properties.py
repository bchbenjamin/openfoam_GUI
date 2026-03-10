import bpy

class ClassyMeshObjectProperties(bpy.types.PropertyGroup):
    is_block: bpy.props.BoolProperty(name="Is Mesh Block", default=False)
    block_type: bpy.props.EnumProperty(
        name="Block Type",
        items=[("box", "Box", ""), ("extrude", "Extrude", ""), ("revolve", "Revolve", "")]
    )
    cells: bpy.props.IntVectorProperty(name="Cells X/Y/Z", default=(10, 10, 10), min=1)
    patch_name: bpy.props.StringProperty(name="Patch Name", default="defaultWall")

class ClassyMeshSceneProperties(bpy.types.PropertyGroup):
    case_path: bpy.props.StringProperty(name="Case Directory", subtype='DIR_PATH')
    bashrc_path: bpy.props.StringProperty(name="OpenFOAM bashrc", default="/opt/openfoam13/etc/bashrc", subtype='FILE_PATH')
