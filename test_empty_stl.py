import bpy
import os
import sys

sys.path.append(os.getcwd())
import addon.properties

bpy.utils.register_class(addon.properties.ClassyFacePatch)
bpy.utils.register_class(addon.properties.ClassyMeshObjectProperties)
bpy.utils.register_class(addon.properties.ClassyMeshSceneProperties)
bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=addon.properties.ClassyMeshObjectProperties)
bpy.types.Scene.classy_mesh_props = bpy.props.PointerProperty(type=addon.properties.ClassyMeshSceneProperties)

import addon.operators
bpy.utils.register_class(addon.operators.CLASSY_OT_generate_mesh)

case_path = "/tmp/test_empty_stl_case"
bpy.context.scene.classy_mesh_props.case_path = case_path

bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.active_object
obj.classy_block_props.block_type = "BOX"
obj.classy_block_props.stl_file = "/tmp/empty.stl"
with open("/tmp/empty.stl", "w") as f: f.write("")
obj.classy_block_props.stl_projection_face = "top"

bpy.ops.classy.generate_mesh()

import subprocess
rc = subprocess.run(["bash", "-c", "source /home/bchbenjamin/OpenFOAM/OpenFOAM-13/etc/bashrc && blockMesh -case " + case_path], capture_output=True, text=True)
print("RC:", rc.returncode)
print(rc.stderr)
