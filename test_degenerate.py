import bpy
import os
import sys
sys.path.append(os.getcwd())
import addon.properties

# Setup classes
bpy.utils.register_class(addon.properties.ClassyFacePatch)
bpy.utils.register_class(addon.properties.ClassyMeshObjectProperties)
bpy.utils.register_class(addon.properties.ClassyMeshSceneProperties)
bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=addon.properties.ClassyMeshObjectProperties)
bpy.types.Scene.classy_mesh_props = bpy.props.PointerProperty(type=addon.properties.ClassyMeshSceneProperties)

import addon.geometry_extractor
import addon.mesh_builder

# Degenerate case (circle at origin revolved around Z)
bpy.ops.curve.primitive_bezier_circle_add()
obj = bpy.context.active_object
obj["classy_sketch"] = 1
obj.classy_block_props.block_type = "REVOLVE"
obj.classy_block_props.revolve_angle = 90.0

ctx = type('MockCtx', (), {'scene': type('MockScene', (), {'objects': [obj]})(), 'evaluated_depsgraph_get': lambda: bpy.context.evaluated_depsgraph_get()})()

try:
    spec = addon.geometry_extractor.extract_geometry(ctx)
    print("Should have thrown error!")
except RuntimeError as e:
    print(f"Success! Caught expected error: {e}")
