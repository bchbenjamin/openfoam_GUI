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
    case_path = "/tmp/test_stl_e2e_case"
    if os.path.exists(case_path):
        shutil.rmtree(case_path)
    os.makedirs(case_path)
    
    # Create a dummy STL file representing a tilted terrain
    dummy_stl = "/tmp/tilted_terrain.stl"
    with open(dummy_stl, "w") as f:
        f.write("solid obj\n  facet normal 0 0 1\n    outer loop\n      vertex -10 -10 5\n      vertex 10 -10 5\n      vertex -10 10 10\n    endloop\n  endfacet\nendsolid obj\n")

    # Create a box and set the STL file
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.classy_block_props.block_type = "BOX"
    obj.classy_block_props.stl_file = dummy_stl
    obj.classy_block_props.stl_projection_face = "top"
    
    # Needs a lot of cells to capture curvature, but for this test we just need the dictionary to be correct.
    
    bpy.context.scene.classy_mesh_props.case_path = case_path
    
    print("Testing valid STL generation...")
    try:
        res = bpy.ops.classy.generate_mesh()
        print("Operator Result:", res)
    except Exception as e:
        print(f"FAILED: Exception running operator: {e}")
        sys.exit(1)
        
    # Check if files were copied
    geom_copied = os.path.isfile(os.path.join(case_path, "constant", "geometry", "tilted_terrain.stl"))
    if not geom_copied:
        print("FAILED: File was not copied to geometry!")
        sys.exit(1)
        
    # Read the blockMeshDict to verify native classy_blocks projection is used
    dict_path = os.path.join(case_path, "system", "blockMeshDict")
    with open(dict_path, "r") as f:
        content = f.read()
        
    # It must contain the geometry declaration
    if "tilted_terrain.stl" not in content or "triSurfaceMesh" not in content:
        print("FAILED: geometry not registered in blockMeshDict!")
        sys.exit(1)
        
    # It must contain the face projection for the top face (face index 4 or 5 depending on block numbering)
    if "project" not in content:
        print("FAILED: 'project' directive not found in blockMeshDict!")
        sys.exit(1)
        
    # Verify OpenFOAM's blockMesh can run it successfully
    import subprocess
    import addon.foam_path_utils
    from addon.foam_runner import run_blockmesh
    
    print("\nRunning blockMesh to verify validity...")
    rc, stdout, stderr = run_blockmesh(case_path, "")
    if rc != 0:
        print(f"FAILED: blockMesh execution failed with code {rc}!")
        print(stderr)
        sys.exit(1)
        
    print("\nSUCCESS! Native projection emitted correct blockMeshDict and ran successfully.")

run_test()

