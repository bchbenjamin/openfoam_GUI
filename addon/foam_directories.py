import os
import getpass
from pathlib import Path
import bpy

def auto_detect_foam_dirs():
    foam_run = os.environ.get('FOAM_RUN', '')
    foam_tutorials = os.environ.get('FOAM_TUTORIALS', '')
    
    # Fallback for FOAM_RUN
    if not foam_run:
        try:
            username = getpass.getuser()
            home_openfoam = Path.home() / "OpenFOAM"
            if home_openfoam.is_dir():
                for item in home_openfoam.iterdir():
                    if item.is_dir() and item.name.startswith(f"{username}-"):
                        run_dir = item / "run"
                        if run_dir.is_dir():
                            foam_run = str(run_dir)
                            break
        except Exception:
            pass

    # Fallback for FOAM_TUTORIALS
    if not foam_tutorials:
        for base_path in ["/opt", "/usr/lib/openfoam"]:
            base = Path(base_path)
            if base.is_dir():
                for item in base.iterdir():
                    if item.is_dir() and "openfoam" in item.name.lower():
                        tut_dir = item / "tutorials"
                        if tut_dir.is_dir():
                            foam_tutorials = str(tut_dir)
                            break
                if foam_tutorials:
                    break

    return foam_run, foam_tutorials

# Auto-detect at module load to set dynamic defaults
_default_foam_run, _default_foam_tutorials = auto_detect_foam_dirs()

class FoamDirectoryProperties(bpy.types.PropertyGroup):
    foam_run_dir: bpy.props.StringProperty(
        name="FOAM_RUN",
        description="Path to your OpenFOAM run directory",
        subtype='DIR_PATH',
        default=_default_foam_run
    )
    foam_tutorials_dir: bpy.props.StringProperty(
        name="FOAM_TUTORIALS",
        description="Path to your OpenFOAM tutorials directory",
        subtype='DIR_PATH',
        default=_default_foam_tutorials
    )

class CLASSY_PT_foam_directories(bpy.types.Panel):
    bl_label = "OpenFOAM Directories"
    bl_idname = "CLASSY_PT_foam_directories"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Classy FOAM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        if _default_foam_run and _default_foam_tutorials:
            layout.label(text="Paths Auto-Detected", icon='INFO')
        elif _default_foam_run or _default_foam_tutorials:
            layout.label(text="Some Paths Auto-Detected", icon='INFO')
        else:
            layout.label(text="Warning: Paths not auto-detected", icon='ERROR')
            
        layout.prop(scene.foam_dirs, "foam_run_dir")
        layout.prop(scene.foam_dirs, "foam_tutorials_dir")

def register():
    bpy.utils.register_class(FoamDirectoryProperties)
    bpy.types.Scene.foam_dirs = bpy.props.PointerProperty(type=FoamDirectoryProperties)
    bpy.utils.register_class(CLASSY_PT_foam_directories)

def unregister():
    bpy.utils.unregister_class(CLASSY_PT_foam_directories)
    del bpy.types.Scene.foam_dirs
    bpy.utils.unregister_class(FoamDirectoryProperties)
