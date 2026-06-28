bl_info = {"name": "Classy Blocks Integration", "category": "Mesh", "blender": (4, 0, 0)}
import bpy
from . import properties, ui, operators, geometry_extractor, vtk_importer, preferences
from . import foam_directories
from . import tutorial_manager
from . import auto_update
from . import dependencies

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
    tutorial_manager.CLASSY_OT_confirm_case_path,
    tutorial_manager.CLASSY_PT_tutorial_manager,
    dependencies.CLASSY_OT_install_python_deps,
    dependencies.CLASSY_OT_install_openfoam,
]


@bpy.app.handlers.persistent
def _on_load_post(filepath):
    """
    Runs after any .blend file loads (including new files).
    Restores the last-used case directory into the scene if the scene
    has no case_path set, so the user never has to re-enter it.
    Also ensures auto-update starts off — it defaults False but existing
    userpref.blend values would override that; we force it off here.
    """
    try:
        prefs = bpy.context.preferences.addons.get(__package__)
        if not prefs:
            return
        p = prefs.preferences
        scene_props = bpy.context.scene.classy_mesh_props

        # Restore case path from last session if the scene has none
        if not scene_props.case_path:
            remembered = p.last_case_dir or p.default_case_dir
            if remembered:
                scene_props.case_path = remembered

        # Force auto-update off on every load (opt-in, never opt-out-less)
        scene_props.use_auto_update = False

    except Exception as e:
        print(f"[classy_blocks] load_post handler error: {e}")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=properties.ClassyMeshObjectProperties)
    bpy.types.Scene.classy_mesh_props = bpy.props.PointerProperty(type=properties.ClassyMeshSceneProperties)
    bpy.types.Scene.foam_dirs = bpy.props.PointerProperty(type=foam_directories.FoamDirectoryProperties)
    bpy.types.Scene.tutorial_manager = bpy.props.PointerProperty(type=tutorial_manager.TutorialManagerProperties)
    auto_update.register()
    dependencies.register_startup_checks()
    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)


def unregister():
    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)
    dependencies.unregister_startup_checks()
    auto_update.unregister()
    del bpy.types.Scene.foam_dirs
    del bpy.types.Scene.tutorial_manager
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.classy_block_props
    del bpy.types.Scene.classy_mesh_props

