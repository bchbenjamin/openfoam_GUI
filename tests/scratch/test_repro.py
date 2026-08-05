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

case_path = "/tmp/test_repro_case"
os.makedirs(case_path, exist_ok=True)

# Create a box and set the STL file
bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.active_object
obj.classy_block_props.block_type = "BOX"
# Use 'x16.stl' as the stl file name, mimicking the user
obj.classy_block_props.stl_file = "/tmp/x16.stl"
# Create a dummy x16.stl
with open("/tmp/x16.stl", "w") as f:
    f.write("solid obj\n  facet normal 0 0 1\n    outer loop\n      vertex 0 0 0\n      vertex 1 0 0\n      vertex 0 1 0\n    endloop\n  endfacet\nendsolid obj\n")

obj.classy_block_props.stl_projection_face = "top"
bpy.context.scene.classy_mesh_props.case_path = case_path

res = bpy.ops.classy.generate_mesh()
print("Operator Result:", res)

with open(os.path.join(case_path, "system", "blockMeshDict"), "r") as f:
    print(f.read())
