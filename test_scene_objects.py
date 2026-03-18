import bpy

bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "MyCube"

bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(5, 0, 0))
plane = bpy.context.active_object
plane.name = "MyPlane"

# Deselect everything
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = None

print("Scene objects with nothing selected:")
for obj in bpy.context.scene.objects:
    print(f"  - {obj.name}")

# Hide Plane
plane.hide_set(True)
print("Scene objects with Plane hidden:")
for obj in bpy.context.scene.objects:
    print(f"  - {obj.name}")

