import bpy
bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
print(f"Original pts: {len(obj.data.splines[0].bezier_points)}")
obj.modifiers.new(name="Preview", type='SCREW')
depsgraph = bpy.context.evaluated_depsgraph_get()
obj_eval = obj.evaluated_get(depsgraph)
data = obj_eval.data
print(f"Eval pts: {len(data.splines[0].bezier_points)}")
