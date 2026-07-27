import bpy
import os
import sys
import shutil

sys.path.append(os.getcwd())
import addon.properties

bpy.utils.register_class(addon.properties.ClassyFacePatch)
bpy.utils.register_class(addon.properties.ClassyMeshObjectProperties)
bpy.utils.register_class(addon.properties.ClassyMeshSceneProperties)
bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=addon.properties.ClassyMeshObjectProperties)
bpy.types.Scene.classy_mesh_props = bpy.props.PointerProperty(type=addon.properties.ClassyMeshSceneProperties)

import addon.operators
bpy.utils.register_class(addon.operators.CLASSY_OT_generate_mesh)

def run_test():
    case_path = "/tmp/test_stl_case"
    if os.path.exists(case_path):
        shutil.rmtree(case_path)
    os.makedirs(case_path)
    
    # Create a dummy STL file somewhere OUTSIDE the case directory
    dummy_stl = "/tmp/dummy_terrain.stl"
    with open(dummy_stl, "w") as f:
        f.write("solid obj\n  facet normal 0 0 1\n    outer loop\n      vertex 0 0 0\n      vertex 1 0 0\n      vertex 0 1 0\n    endloop\n  endfacet\nendsolid obj\n")

    # Create a box and set the STL file
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.classy_block_props.block_type = "BOX"
    obj.classy_block_props.stl_file = dummy_stl
    obj.classy_block_props.stl_projection_face = "top"
    
    bpy.context.scene.classy_mesh_props.case_path = case_path
    
    print("Testing valid STL generation...")
    try:
        res = bpy.ops.classy.generate_mesh()
        print("Operator Result:", res)
    except Exception as e:
        print(f"FAILED: Exception running operator: {e}")
        sys.exit(1)
        
    # Check if files were copied
    geom_copied = os.path.isfile(os.path.join(case_path, "constant", "geometry", "dummy_terrain.stl"))
    tri_copied = os.path.isfile(os.path.join(case_path, "constant", "triSurface", "dummy_terrain.stl"))
    print(f"Copied to geometry/? {geom_copied}")
    print(f"Copied to triSurface/? {tri_copied}")
    
    if not (geom_copied and tri_copied):
        print("FAILED: Files were not copied!")
        sys.exit(1)
        
    # Testing missing STL
    print("\nTesting missing STL generation...")
    obj.classy_block_props.stl_file = "/tmp/does_not_exist.stl"
    try:
        # The operator returns {'CANCELLED'} which raises an exception in bpy.ops
        bpy.ops.classy.generate_mesh()
        print("FAILED: Operator did not cancel on missing STL!")
        sys.exit(1)
    except RuntimeError as e:
        print("Operator Result: cancelled as expected.")
        
    print("\nSUCCESS!")

run_test()

