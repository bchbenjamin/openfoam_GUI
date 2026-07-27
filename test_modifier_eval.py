import bpy
bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
obj.modifiers.new(name="Preview", type='SCREW')
depsgraph = bpy.context.evaluated_depsgraph_get()
obj_eval = obj.evaluated_get(depsgraph)
data = obj_eval.data
print(f"Original type: {type(obj.data)}")
print(f"Evaluated type: {type(data)}")
try:
    print(f"Has splines? {hasattr(data, 'splines')}")
except Exception as e:
    print(e)
