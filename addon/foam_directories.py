"""
OpenFOAM Directory Management.

Handles user preferences for system-wide OpenFOAM installations and aliases,
ensuring the add-on can correctly invoke terminal commands like blockMesh.
"""

import os
import getpass
from pathlib import Path
import bpy

def auto_detect_foam_dirs():
    foam_run = os.environ.get('FOAM_RUN', '')
    foam_tutorials = os.environ.get('FOAM_TUTORIALS', '')
    
    if not foam_run or not foam_tutorials:
        import subprocess
        username = getpass.getuser()
        common_bashrcs = [
            f"/home/{username}/OpenFOAM/OpenFOAM-13/etc/bashrc",
            f"/home/{username}/OpenFOAM/{username}-13/etc/bashrc",
            "/opt/openfoam13/etc/bashrc"
        ]
        
        for bashrc in common_bashrcs:
            if os.path.exists(bashrc):
                try:
                    if not foam_run:
                        res = subprocess.run(["bash", "-c", f"source {bashrc} && echo $FOAM_RUN"], capture_output=True, text=True)
                        if res.returncode == 0 and res.stdout.strip():
                            foam_run = res.stdout.strip()
                    if not foam_tutorials:
                        res = subprocess.run(["bash", "-c", f"source {bashrc} && echo $FOAM_TUTORIALS"], capture_output=True, text=True)
                        if res.returncode == 0 and res.stdout.strip():
                            foam_tutorials = res.stdout.strip()
                            
                    if foam_run and foam_tutorials:
                        break
                except Exception:
                    pass

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
