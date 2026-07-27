import bpy
bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
obj["classy_sketch"] = 1
import addon
from addon.properties import ClassyBlockProperties
# Wait, addon is already loaded if we load the full addon?
# The user's env has syntax error in __init__.py so it failed to load. Let's fix that syntax error first!
