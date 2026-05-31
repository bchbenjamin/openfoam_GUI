import bpy
from mathutils import Vector
import os
import sys

# Add addon directory to path so we can import geometry_extractor
addon_dir = os.path.join(os.path.dirname(bpy.data.filepath), "addon")
if addon_dir not in sys.path:
    sys.path.append(addon_dir)

import geometry_extractor

def test_extract_geometry():
    # 1. Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Add cube and tag as block
    bpy.ops.mesh.primitive_cube_add(size=2, location=(1, 2, 3), rotation=(0, 0, 0))
    obj = bpy.context.active_object
    obj.classy_block_props.is_block = True
    obj.classy_block_props.block_type = "box"
    obj.classy_block_props.cells = (10, 10, 10)

    # 3. Rotate and scale to test world matrix
    obj.scale = (1, 2, 3)
    obj.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()

    # Cube starts at -1..1 sizes, so corners are +/- 1 before scale.
    # After scale(1,2,3): -1..1, -2..2, -3..3
    # After loc(1,2,3): 0..2, 0..4, 0..6
    
    # 4. Extract
    spec = geometry_extractor.extract_geometry(bpy.context)
    
    # 5. Assert blocks
    assert len(spec["blocks"]) == 1
    block = spec["blocks"][0]
    
    assert block["type"] == "box"
    assert "cells" in block
    assert block["cells"] == [10, 10, 10]
    
    p_min = block["p_min"]
    p_max = block["p_max"]

    assert all(abs(a - b) < 1e-4 for a, b in zip(p_min, [0, 0, 0]))
    assert all(abs(a - b) < 1e-4 for a, b in zip(p_max, [2, 4, 6]))
    
    print("[TEST PASSED] Geometry extraction correctly handles Blender world matrices!")

if __name__ == "__main__":
    test_extract_geometry()
