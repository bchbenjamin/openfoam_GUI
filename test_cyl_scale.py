import bpy
import sys
import os

sys.path.append("/home/bchbenjamin/classy_blender_mesh/addon")
import geometry_extractor

def test_cylinder_scale():
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2)
    obj = bpy.context.active_object
    obj.scale = (2.0, 0.5, 1.0)
    bpy.context.view_layer.update()
    
    spec = geometry_extractor.extract_geometry(bpy.context)
    print("Blocks:", spec["blocks"])
    print("Warnings:", spec["warnings"])

if __name__ == "__main__":
    test_cylinder_scale()
