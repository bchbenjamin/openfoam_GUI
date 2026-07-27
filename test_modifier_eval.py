import bpy

bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
mod = obj.modifiers.new(name="Screw", type='SCREW')
mod.angle = 0
mod.screw_offset = 2.0

depsgraph = bpy.context.evaluated_depsgraph_get()
obj_eval = obj.evaluated_get(depsgraph)
data = obj_eval.data
print("Data type:", type(data))
print("Has splines?", hasattr(data, 'splines'))

