import bpy

bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2)
obj = bpy.context.active_object
obj.scale = (2.0, 0.5, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

verts = [v.co for v in obj.data.vertices]
z_coords = [v.z for v in verts]
z_min = min(z_coords)
z_min_verts = [v for v in verts if abs(v.z - z_min) < 1e-4]
print("z_min_verts len:", len(z_min_verts))
