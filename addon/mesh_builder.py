"""
addon/mesh_builder.py
Calls classy_blocks API to build blockMeshDict from a geometry spec dict.
No Blender imports — fully testable with plain Python/pytest.

UNIVERSAL APPROACH:
  Every block is a cb.Box(p_min, p_max).
  Non-box shapes get all 6 faces projected onto their own STL surface,
  making the structured hex mesh conform to the original geometry.

CRITICAL API NOTE:
  CORRECT:   mesh.add(block)      <- always use this
  WRONG:     mesh.merge(block)    <- does NOT exist in classy_blocks 1.x

CALLED BY: operators.py -> CLASSY_OT_generate_mesh.execute()
"""

import os
import classy_blocks as cb
from typing import Dict, Any

ALL_FACES = ["bottom", "top", "front", "back", "left", "right"]


def _apply_chops(block, spec: Dict[str, Any]) -> None:
    """
    Applies cell chopping (count + grading) to a block in all 3 axes.

    Dispatches by grading_type:
      - RATIO:      use c2c_expansion from spec["grading"]
      - START_SIZE:  use start_size (first cell width)
      - SYMMETRIC:   use start_size + end_size (first and last cell width)
    """
    grading_type = spec.get("grading_type", "RATIO")
    cells = spec["cells"]
    grading = spec.get("grading", [1.0, 1.0, 1.0])
    start_size = spec.get("start_size", 1e-4)
    end_size = spec.get("end_size", 1e-4)

    for axis in range(3):
        if grading_type == "START_SIZE":
            block.chop(axis, count=cells[axis], start_size=start_size)
        elif grading_type == "SYMMETRIC":
            block.chop(axis, start_size=start_size, end_size=end_size)
        else:
            block.chop(axis, count=cells[axis],
                       c2c_expansion=grading[axis])


def build_block(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds a single block from a spec dict and adds it to the mesh.

    Every block is a cb.Box. Non-box shapes have their faces projected
    onto their own STL to conform the hex mesh to the original geometry.
    """
    block_name = spec.get("name", "unnamed")
    stl_name = spec.get("self_stl_name", "")
    needs_projection = spec.get("needs_self_projection", False)

    print(f"[classy_blocks]   Building Box: p_min={spec['p_min']}, p_max={spec['p_max']}")
    box = cb.Box(spec["p_min"], spec["p_max"])
    _apply_chops(box, spec)

    # Self-projection: project all 6 faces onto the object's own STL
    if needs_projection and stl_name:
        print(f"[classy_blocks]   Projecting ALL 6 faces onto '{stl_name}'")
        for face in ALL_FACES:
            box.project_side(face, stl_name)
            print(f"[classy_blocks]     → projected '{face}'")

    # User-specified STL projection (from UI, e.g., terrain)
    user_projections = spec.get("stl_projections", {})
    for face_name, user_stl in user_projections.items():
        box.project_side(face_name, user_stl)
        print(f"[classy_blocks]   User projection: '{face_name}' → '{user_stl}'")

    mesh.add(box)
    print(f"[classy_blocks]   Block '{block_name}' added to mesh")


def build_from_spec(spec: Dict[str, Any], output_path: str) -> None:
    """
    Takes a geometry spec dict and writes a blockMeshDict to output_path.

    This is the main entry point called by the Blender addon operators.
    It creates a cb.Mesh(), adds all blocks, then calls mesh.write().
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.isdir(output_dir):
        raise IOError(
            f"Output directory does not exist:{output_dir}\n"
            "Create it with: mkdir -p " + output_dir
        )

    mesh = cb.Mesh()

    for block_spec in spec["blocks"]:
        block_name = block_spec.get("name", "unnamed")
        grading_type = block_spec.get("grading_type", "RATIO")
        print(f"[classy_blocks] Building block: '{block_name}' "
              f"(grading: {grading_type})")
        build_block(mesh, block_spec)

    print(f"[classy_blocks] Writing blockMeshDict to: {output_path}")
    mesh.write(output_path)
    print(f"[classy_blocks] Written blockMeshDict: {output_path} "
          f"({os.path.getsize(output_path)} bytes)")
