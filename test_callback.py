import bpy
import math
bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
obj["classy_sketch"] = 1

def update_sketch_preview(self, context):
    print(f"Callback triggered! Block type: {self.block_type}")
    obj = context.active_object
    if not (obj and obj.type == 'CURVE' and obj.get("classy_sketch")):
        return
    for m in list(obj.modifiers):
        if m.name.startswith("(Preview)"):
            obj.modifiers.remove(m)
    if self.block_type == "EXTRUDE":
        mod = obj.modifiers.new(name="(Preview) Extrude", type='SCREW')
        mod.angle = 0
        mod.screw_offset = self.extrude_distance
        mod.axis = self.extrude_axis
    elif self.block_type == "REVOLVE":
        mod = obj.modifiers.new(name="(Preview) Revolve", type='SCREW')
        mod.angle = math.radians(self.revolve_angle)
        mod.screw_offset = 0
        mod.axis = self.revolve_axis

bpy.types.Object.my_prop = bpy.props.EnumProperty(
    items=[("BOX", "Box", ""), ("EXTRUDE", "Extrude", ""), ("REVOLVE", "Revolve", "")],
    default="BOX",
    update=update_sketch_preview
)
bpy.types.Object.extrude_distance = bpy.props.FloatProperty(default=1.0, update=update_sketch_preview)
bpy.types.Object.extrude_axis = bpy.props.EnumProperty(items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")], default="Z", update=update_sketch_preview)
bpy.types.Object.revolve_angle = bpy.props.FloatProperty(default=90.0, update=update_sketch_preview)
bpy.types.Object.revolve_axis = bpy.props.EnumProperty(items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")], default="Z", update=update_sketch_preview)

obj.my_prop = "EXTRUDE"
print("Modifiers:", [m.name for m in obj.modifiers])
obj.extrude_distance = 2.0
print("Extrude distance updated")
obj.my_prop = "REVOLVE"
print("Modifiers:", [m.name for m in obj.modifiers])

