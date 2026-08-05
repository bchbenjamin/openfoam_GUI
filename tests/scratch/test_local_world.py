import bpy
import mathutils

bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
obj.location = (10, 0, 0)
depsgraph = bpy.context.evaluated_depsgraph_get()
obj_eval = obj.evaluated_get(depsgraph)
print("Local co:", obj_eval.data.splines[0].bezier_points[0].co)
