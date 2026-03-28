"""
addon/mesh_builder.py
Calls classy_blocks API to build blockMeshDict from a geometry spec dict.
No Blender imports — fully testable with plain Python/pytest.

CRITICAL API NOTE:
  CORRECT:   mesh.add(block)      ← always use this
  WRONG:     mesh.merge(block)    ← does NOT exist in classy_blocks 1.x

HOW THE SPEC DICT WORKS:
  spec = {
    "blocks": [
      {
        "type": "box",            # "box", "extrude", or "revolve"
        "name": "main_block",     # for logging
        "p_min": [0, 0, 0],       # (box only) minimum corner
        "p_max": [1, 1, 1],       # (box only) maximum corner
        "cells": [10, 10, 10],    # cell count per axis direction
        "grading": [1.0, 1.0, 1.0], # c2c expansion ratio per direction (1.0 = uniform)
        "grading_type": "RATIO",  # "RATIO", "START_SIZE", or "SYMMETRIC"
        "start_size": 1e-4,       # first cell size (used when grading_type != RATIO)
        "end_size": 1e-4,         # last cell size (used when grading_type == SYMMETRIC)
      }
    ],
    "merge_tolerance": 1e-4       # vertices closer than this are merged
  }

CALLED BY: operators.py → CLASSY_OT_generate_mesh.execute()
"""

import os
import math
import classy_blocks as cb
from typing import Dict, Any


def _apply_chops(block, spec: Dict[str, Any]) -> None:
    """
    Applies cell chopping (count + grading) to a block in all 3 axes.

    Dispatches by grading_type:
      - RATIO:      use c2c_expansion from spec["grading"]
      - START_SIZE:  use start_size (first cell width)
      - SYMMETRIC:   use start_size + end_size (first and last cell width)

    This is shared by all block types (box, extrude, revolve).
    """
    grading_type = spec.get("grading_type", "RATIO")
    cells = spec["cells"]
    grading = spec.get("grading", [1.0, 1.0, 1.0])
    start_size = spec.get("start_size", 1e-4)
    end_size = spec.get("end_size", 1e-4)

    for axis in range(3):
        if grading_type == "START_SIZE":
            # 2 params: count + start_size
            block.chop(axis, count=cells[axis], start_size=start_size)
        elif grading_type == "SYMMETRIC":
            # 2 params: start_size + end_size (count is auto-computed)
            block.chop(axis, start_size=start_size, end_size=end_size)
        else:
            # RATIO (default) — 2 params: count + c2c_expansion
            block.chop(axis, count=cells[axis],
                       c2c_expansion=grading[axis])


def build_box_block(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Adds a rectangular Box block to the mesh.

    cb.Box(p_min, p_max):
      p_min — [x, y, z] of the bottom-left-back corner
      p_max — [x, y, z] of the top-right-front corner

    Grading is applied via _apply_chops() based on spec["grading_type"].
    """
    box = cb.Box(spec["p_min"], spec["p_max"])
    _apply_chops(box, spec)

    # Apply STL projections if specified
    stl_projections = spec.get("stl_projections", {})
    for face_name, stl_name in stl_projections.items():
        box.project_face(face_name, stl_name)
        print(f"[classy_blocks]   Projecting face '{face_name}' onto '{stl_name}'")

    # CORRECT: mesh.add() — NOT mesh.merge()
    mesh.add(box)


def build_extrude_block(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Adds an Extrude block to the mesh.
    cb.Extrude(face, extrude_vector):
      face — a list of 4 [x,y,z] points defining the base quadrilateral
      extrude_vector — [dx, dy, dz] direction and length of the extrusion
    """
    face = cb.Face(spec["face"])
    extrude = cb.Extrude(face, spec["extrude_vector"])
    _apply_chops(extrude, spec)
    mesh.add(extrude)


def build_revolve_block(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Adds a Revolve block to the mesh.
    cb.Revolve(face, angle, axis, origin):
      face   — 4-point quadrilateral to revolve
      angle  — rotation angle in RADIANS (we convert from degrees)
      axis   — [dx, dy, dz] axis vector
      origin — [x, y, z] point on the axis
    """
    angle_radians = math.radians(spec["angle"])
    face = cb.Face(spec["face"])
    revolve = cb.Revolve(
        face,
        angle_radians,
        spec["axis"],
        spec["origin"],
    )
    _apply_chops(revolve, spec)
    mesh.add(revolve)


def build_from_spec(spec: Dict[str, Any], output_path: str) -> None:
    """
    Takes a geometry spec dict and writes a blockMeshDict to output_path.

    This is the main entry point called by the Blender addon operators.
    It creates a cb.Mesh(), adds all blocks, then calls mesh.write().
    """
    # Validate that the output directory exists before we start building,
    # so we fail fast with a clear error message rather than after all
    # the block-building work is done.
    output_dir = os.path.dirname(output_path)
    if not os.path.isdir(output_dir):
        raise IOError(
            f"Output directory does not exist:{output_dir}\n"
            "Create it with: mkdir -p " + output_dir
        )

    # cb.Mesh() is the top-level container. All blocks are added to it.
    mesh = cb.Mesh()

    for block_spec in spec["blocks"]:
        block_type = block_spec["type"]
        block_name = block_spec.get("name", "unnamed")
        grading_type = block_spec.get("grading_type", "RATIO")
        print(f"[classy_blocks] Building {block_type} block: '{block_name}' "
              f"(grading: {grading_type})")

        if block_type == "box":
            build_box_block(mesh, block_spec)
        elif block_type == "extrude":
            build_extrude_block(mesh, block_spec)
        elif block_type == "revolve":
            build_revolve_block(mesh, block_spec)
        else:
            raise ValueError(f"Unknown block type '{block_type}' for block '{block_name}'")

    # mesh.write() performs vertex merging (within tolerance), assigns global
    # vertex indices, and writes the blockMeshDict file.
    mesh.write(output_path)
    print(f"[classy_blocks] Written blockMeshDict:{output_path} ({os.path.getsize(output_path)} bytes)")
