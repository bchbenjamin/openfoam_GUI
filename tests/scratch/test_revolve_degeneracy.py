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

import addon.geometry_extractor
import addon.mesh_builder
import addon.foam_runner
import addon.case_setup

def run_test(name, plane_rot, offset, axis_str, expect_success) -> None:
    """

    Args:
      name: 
      plane_rot: 
      offset: 
      axis_str: 
      expect_success: 

    Returns:

    """
    bpy.ops.curve.primitive_bezier_circle_add()
    obj = bpy.context.active_object
    
    bpy.ops.object.mode_set(mode='EDIT')
    if plane_rot:
        bpy.ops.transform.rotate(value=plane_rot[0], orient_axis=plane_rot[1])
    bpy.ops.transform.translate(value=offset)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    obj["classy_sketch"] = 1
    props = obj.classy_block_props
    props.block_type = "REVOLVE"
    props.revolve_angle = 90.0
    props.revolve_axis = axis_str
    
    ctx = type('MockCtx', (), {'scene': type('MockScene', (), {'objects': [obj], 'classy_mesh_props': type('P', (), {'case_path': f'/tmp/reg_{name}'})()})(), 'evaluated_depsgraph_get': lambda: bpy.context.evaluated_depsgraph_get()})()
    
    success = False
    try:
        spec = addon.geometry_extractor.extract_geometry(ctx)
        
        case_dir = f"/tmp/reg_{name}"
        os.makedirs(os.path.join(case_dir, "system"), exist_ok=True)
        dict_path = os.path.join(case_dir, "system", "blockMeshDict")
        
        addon.mesh_builder.build_from_spec(spec, dict_path)
        addon.case_setup.setup_incompressible_case(case_dir, [])
        
        code, stdout, stderr = addon.foam_runner.run_blockmesh(case_dir, "")
        success = (code == 0)
        res = "SUCCESS" if success else "FAILED (blockMesh)"
    except RuntimeError as e:
        res = f"FAILED (extraction validation): {e}"
        
    print(f"[{name}] {res}")
    if success != expect_success:
        print(f"  --> ERROR: Expected success={expect_success}, got {success}")
        sys.exit(1)
        
    bpy.data.objects.remove(obj)

# 1. XY Plane (default). Normal=Z. Revolve=Z. Always sweeps its own plane (0 volume).
run_test("XY_Z_Degenerate", None, (2,0,0), "Z", False)

# 2. XY Plane (default). Normal=Z. Revolve=X. Offset along Y. Sweep=Z. Valid!
run_test("XY_X_Valid", None, (0,2,0), "X", True)

# 3. XY Plane (default). Normal=Z. Revolve=X. Offset along X. Sweep=0. Self-intersecting!
run_test("XY_X_ZeroSweep", None, (2,0,0), "X", False)

# 4. YZ Plane. Normal=X. Revolve=Z. Offset along Y. Sweep=-X. Valid!
run_test("YZ_Z_Valid", (1.5708, 'Y'), (0,2,0), "Z", True)

# 5. XZ Plane. Normal=Y. Revolve=Z. Offset along X. Sweep=Y. Valid!
run_test("XZ_Z_Valid", (1.5708, 'X'), (2,0,0), "Z", True)

print("All tests passed!")
