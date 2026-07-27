import bpy
import os
import sys
sys.path.append(os.getcwd())
import addon.properties

# Setup necessary classes
bpy.utils.register_class(addon.properties.ClassyFacePatch)
bpy.utils.register_class(addon.properties.ClassyMeshObjectProperties)
bpy.utils.register_class(addon.properties.ClassyMeshSceneProperties)
bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=addon.properties.ClassyMeshObjectProperties)
bpy.types.Scene.classy_mesh_props = bpy.props.PointerProperty(type=addon.properties.ClassyMeshSceneProperties)

from addon.geometry_extractor import extract_geometry
from addon import foam_runner
from addon import mesh_builder
from addon import case_setup

# Create wrong-wound sketch
bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
obj["classy_sketch"] = 1
props = obj.classy_block_props
props.block_type = "REVOLVE"
props.revolve_angle = -90.0

pts = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 0.0, 1.0], [1.0, 0.0, 1.0]]

curve = obj.data
curve.splines.clear()
spline = curve.splines.new('POLY')
spline.points.add(3)
for i, p in enumerate(pts):
    spline.points[i].co = (*p, 1.0)

ctx = type('MockCtx', (), {'scene': type('MockScene', (), {'objects': [obj], 'classy_mesh_props': type('P', (), {'case_path': '/tmp/test_revolve_case'})()})(), 'evaluated_depsgraph_get': lambda: bpy.context.evaluated_depsgraph_get()})()

# Extract
res = extract_geometry(ctx)
assert len(res["blocks"]) == 1

# Write to blockMeshDict
case_dir = "/tmp/test_revolve_case"
os.makedirs(case_dir, exist_ok=True)
os.makedirs(os.path.join(case_dir, "system"), exist_ok=True)
import shutil
dict_path = os.path.join(case_dir, "system", "blockMeshDict")

mesh_builder.build_from_spec(res, dict_path)
case_setup.setup_incompressible_case(case_dir, [])

# Run blockMesh
import subprocess
try:
    code, stdout, stderr = foam_runner.run_blockmesh(case_dir, "")
    if code != 0:
        print("blockMesh failed!")
        print(stderr)
        sys.exit(1)
    print("blockMesh succeeded!")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

