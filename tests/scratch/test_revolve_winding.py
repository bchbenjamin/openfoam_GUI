import bpy
import sys, os
sys.path.append(os.getcwd())
import addon.properties

bpy.utils.register_class(addon.properties.ClassyFacePatch)
bpy.utils.register_class(addon.properties.ClassyMeshObjectProperties)
bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=addon.properties.ClassyMeshObjectProperties)

from addon import geometry_extractor

bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
obj["classy_sketch"] = 1
obj.classy_block_props.block_type = "REVOLVE"

pts = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 0.0, 1.0], [1.0, 0.0, 1.0]]
curve = obj.data
curve.splines.clear()
spline = curve.splines.new('POLY')
spline.points.add(3)
for i, p in enumerate(pts):
    spline.points[i].co = (*p, 1.0)

mock_ctx = type('MockCtx', (), {'scene': type('MockScene', (), {'objects': [obj]})(), 'evaluated_depsgraph_get': lambda: bpy.context.evaluated_depsgraph_get()})()

print("Original:", pts)

obj.classy_block_props.revolve_angle = 90.0
res = geometry_extractor.extract_geometry(mock_ctx)
print("Extracted (90):", res["blocks"][0]["face"])

obj.classy_block_props.revolve_angle = -90.0
res2 = geometry_extractor.extract_geometry(mock_ctx)
print("Extracted (-90):", res2["blocks"][0]["face"])
