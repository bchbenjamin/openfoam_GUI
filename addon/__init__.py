bl_info = {"name": "Classy Blocks Integration", "category": "Mesh", "blender": (4, 0, 0)}
import bpy
from . import properties, ui, operators, geometry_extractor, vtk_importer, preferences
from . import foam_directories
from . import tutorial_manager
from . import auto_update

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
    operators.CLASSY_OT_run_all,
    foam_directories.FoamDirectoryProperties,
    foam_directories.CLASSY_PT_foam_directories,
    tutorial_manager.TutorialManagerProperties,
    tutorial_manager.CLASSY_OT_search_tutorials,
    tutorial_manager.CLASSY_OT_copy_tutorial,
    tutorial_manager.CLASSY_PT_tutorial_manager,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=properties.ClassyMeshObjectProperties)
    bpy.types.Scene.classy_mesh_props = bpy.props.PointerProperty(type=properties.ClassyMeshSceneProperties)
    bpy.types.Scene.foam_dirs = bpy.props.PointerProperty(type=foam_directories.FoamDirectoryProperties)
    bpy.types.Scene.tutorial_manager = bpy.props.PointerProperty(type=tutorial_manager.TutorialManagerProperties)
    auto_update.register()

def unregister():
    auto_update.unregister()
    del bpy.types.Scene.foam_dirs
    del bpy.types.Scene.tutorial_manager
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.classy_block_props
    del bpy.types.Scene.classy_mesh_props
