bl_info = {"name": "Classy Blocks Integration", "category": "Mesh", "blender": (4, 0, 0)}
import bpy
from . import properties, ui, operators, geometry_extractor, vtk_importer, preferences

classes = [
    preferences.ClassyBlocksPreferences,
    properties.ClassyMeshObjectProperties,
    properties.ClassyMeshSceneProperties,
    ui.CLASSY_PT_main_panel,
    operators.CLASSY_OT_generate_mesh,
    operators.CLASSY_OT_run_blockmesh,
    operators.CLASSY_OT_convert_vtk,
    operators.CLASSY_OT_reload_mesh,
    operators.MESH_OT_export_terrain_stl,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=properties.ClassyMeshObjectProperties)
    bpy.types.Scene.classy_mesh_props = bpy.props.PointerProperty(type=properties.ClassyMeshSceneProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.classy_block_props
    del bpy.types.Scene.classy_mesh_props
