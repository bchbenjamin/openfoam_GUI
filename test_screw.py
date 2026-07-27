import bpy
bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
mod = obj.modifiers.new(name="(Preview) Extrude", type='SCREW')
mod.angle = 0
mod.screw_offset = 2.0
mod.axis = 'Z'

mod2 = obj.modifiers.new(name="(Preview) Revolve", type='SCREW')
mod2.angle = 3.14159
mod2.screw_offset = 0
mod2.axis = 'X'
print("Screw modifiers added successfully")
