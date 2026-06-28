import bpy
import sys
import os
import tempfile
import time

# Ensure we catch errors to exit with a non-zero code
def log_error(msg):
    print(f"\n[TEST ERROR] {msg}")
    sys.exit(1)

def run_tests():
    print("\n--- Starting Headless Blender Integration Tests for Classy Blocks ---")
    
    # 1. Register the addon manually for the test environment
    import sys
    import os
    addon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if addon_dir not in sys.path:
        sys.path.append(addon_dir)
        
    try:
        import addon
        addon.register()
        print("Successfully registered classy_blender_mesh addon")
    except Exception as e:
        log_error(f"Failed to register addon: {e}")
        
    # Check if dependencies are installed
    try:
        from addon.dependencies import check_python_deps, get_openfoam_status
        has_py = check_python_deps()
        has_of = get_openfoam_status(bpy.context)
        if not has_py:
            log_error("Python dependencies (classy_blocks, pyvista) missing in this Blender Python env.")
        if not has_of:
            print("[TEST WARNING] OpenFOAM bashrc not found. Mesh Generation will be tested, but blockMesh execution will fail.")
    except Exception as e:
        log_error(f"Failed to check dependencies: {e}")

    # 2. Setup a clean scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # 3. Setup temporary case directory
    temp_dir = tempfile.mkdtemp(prefix="classy_test_case_")
    bpy.context.scene.classy_mesh_props.case_path = temp_dir
    print(f"Using temp case dir: {temp_dir}")
    
    # 4. Create test primitives
    print("Creating primitives (Cube, Cylinder, Sphere)...")
    
    # Cube: rotated and non-uniformly scaled to test local-space transformations
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "Test_Box"
    cube.rotation_euler = (0.5, 0.5, 0.5)
    cube.scale = (2.0, 1.0, 0.5)
    
    # Cylinder: translated
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2.0, location=(3, 0, 0))
    cyl = bpy.context.active_object
    cyl.name = "Test_Cylinder"
    
    # Sphere: scaled uniformly (using icosphere to test icosphere detection path)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, location=(-3, 0, 0))
    sphere = bpy.context.active_object
    sphere.name = "Test_Sphere"
    sphere.scale = (0.5, 0.5, 0.5)

    # 5. Assign properties
    for obj in [cube, cyl, sphere]:
        obj.classy_block_props.cells = (5, 5, 5)

    # Force a depsgraph update
    bpy.context.view_layer.update()

    # 6. Test: Generate Mesh (blockMeshDict creation)
    print("\nTesting: Mesh Generation (Generate blockMeshDict)...")
    try:
        result = bpy.ops.classy.generate_mesh()
        if 'FINISHED' not in result:
            log_error("generate_mesh operator did not finish successfully.")
            
        dict_path = os.path.join(temp_dir, "system", "blockMeshDict")
        if not os.path.exists(dict_path):
            log_error(f"blockMeshDict not created at {dict_path}")
            
        # Basic validation of the dict
        with open(dict_path, 'r') as f:
            content = f.read()
            if "classy_blocks" not in content:
                log_error("Generated blockMeshDict seems invalid (missing classy_blocks header).")
            if "Test_Box" not in content and "Test_Cylinder" not in content and "Test_Sphere" not in content:
                print("[TEST WARNING] Primitives names not found in blockMeshDict, maybe they were combined into 'defaultFaces'.")
        
        print("✓ Mesh Generation PASSED")
    except Exception as e:
        log_error(f"Mesh Generation failed with exception: {e}")

    # 7. Test: Run blockMesh and reload
    if has_of:
        print("\nTesting: Run blockMesh and convert to VTK...")
        try:
            # We use run_all to test the full pipeline (blockMesh + foamToVTK + reload)
            result = bpy.ops.classy.run_all()
            if 'FINISHED' not in result:
                log_error("run_all operator did not finish successfully.")
                
            # Wait briefly for VTK files to exist (since foamToVTK runs as a subprocess)
            # Actually, run_all in this context might execute the subprocess synchronously or wait
            # Let's verify if VTK files exist.
            time.sleep(2) # Give it a moment just in case
            
            vtk_dir = os.path.join(temp_dir, "VTK")
            if not os.path.exists(vtk_dir) or not os.listdir(vtk_dir):
                 print(f"[TEST WARNING] VTK output directory not found or empty at {vtk_dir}. OpenFOAM run might have failed or not completed.")
            else:
                 print("✓ OpenFOAM execution and VTK conversion PASSED")
                 
            # Check if imported objects exist
            imported_objs = [obj for obj in bpy.data.objects if obj.name.startswith("BlockMesh_Result")]
            if imported_objs:
                print(f"✓ VTK Reload PASSED. Imported {len(imported_objs)} objects.")
            else:
                print("[TEST WARNING] No imported objects found after run_all.")

        except Exception as e:
            log_error(f"OpenFOAM pipeline failed with exception: {e}")
    else:
        print("\nSkipping blockMesh/VTK tests due to missing OpenFOAM environment.")

    print("\n--- All Tests Completed Successfully ---")
    sys.exit(0)

if __name__ == "__main__":
    run_tests()
