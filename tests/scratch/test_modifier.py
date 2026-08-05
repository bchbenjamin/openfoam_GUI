import bpy
bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
mod = obj.modifiers.new(name="Screw", type='SCREW')
print("Modifier axis default:", mod.axis)
