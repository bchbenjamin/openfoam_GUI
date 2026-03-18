# addon/mesh_builder.py
# Calls classy_blocks API to build blockMeshDict from a geometry spec dict.
# No Blender imports — fully testable with plain Python/pytest.
#
# CRITICAL APINOTE:
#   CORRECT:   mesh.add(block)      ← always use this
#   WRONG:     mesh.merge(block)    ← does NOT exist in classy_blocks 1.x
#
# HOW THE SPEC DICT WORKS:
#   spec = {
#     "blocks": [
#       {
#         "type": "box",            # "box", "extrude", or "revolve"
#         "name": "main_block",     # for logging
#         "p_min": [0, 0, 0],       # (box only) minimum corner
#         "p_max": [1, 1, 1],       # (box only) maximum corner
#         "cells": [10, 10, 10],    # cell count per axis direction
#         "grading": [1.0, 1.0, 1.0], # c2c expansion ratio per direction (1.0 = uniform)
#       }
#     ],
#     "merge_tolerance": 1e-4       # vertices closer than this are merged
#   }

import os
import math
import classy_blocks as cb
from typing import Dict, Any

def build_box_block(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Adds a rectangular Box block to the mesh.

    cb.Box(p_min, p_max):
      p_min — [x, y, z] of the bottom-left-back corner
      p_max — [x, y, z] of the top-right-front corner

    .chop(direction, count, c2c_expansion):
      direction 0 = x, 1 = y, 2 = z
      c2c_expansion = 1.0 means uniform cells; >1.0 means cells grow in that direction
    """
    box = cb.Box(spec["p_min"], spec["p_max"])
    box.chop(0, count=spec["cells"][0], c2c_expansion=spec["grading"][0])
    box.chop(1, count=spec["cells"][1], c2c_expansion=spec["grading"][1])
    box.chop(2, count=spec["cells"][2], c2c_expansion=spec["grading"][2])
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
    extrude.chop(0, count=spec["cells"][0], c2c_expansion=spec["grading"][0])
    extrude.chop(1, count=spec["cells"][1], c2c_expansion=spec["grading"][1])
    extrude.chop(2, count=spec["cells"][2], c2c_expansion=spec["grading"][2])
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
    revolve.chop(0, count=spec["cells"][0], c2c_expansion=spec["grading"][0])
    revolve.chop(1, count=spec["cells"][1], c2c_expansion=spec["grading"][1])
    revolve.chop(2, count=spec["cells"][2], c2c_expansion=spec["grading"][2])
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
        print(f"Building{block_type} block: '{block_name}'")

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
    # tolerance = spec.get("merge_tolerance", 1e-4)
    mesh.write(output_path)#, tolerance=tolerance)
    print(f"Written blockMeshDict:{output_path} ({os.path.getsize(output_path)} bytes)")

# ADVANCED FEATURES
# In build_box_block(), after creating the box:
# If the block spec has an stl_projection key, project faces onto it.

def build_box_block_with_stl(mesh, spec):
    """
    Builds a Box block and optionally projects specified faces onto an STL.

    spec format:
    {
        ...normal box spec...,
        "stl_projections": {
            "top": "terrain.stl",   # face name → STL filename in triSurface/
            "front": "wall.stl",
        }
    }
    """
    box = cb.Box(spec["p_min"], spec["p_max"])
    box.chop(0, count=spec["cells"][0], c2c_expansion=spec["grading"][0])
    box.chop(1, count=spec["cells"][1], c2c_expansion=spec["grading"][1])
    box.chop(2, count=spec["cells"][2], c2c_expansion=spec["grading"][2])

    # Apply STL projections if specified
    stl_projections = spec.get("stl_projections", {})
    for face_name, stl_name in stl_projections.items():
        # project_face tells blockMesh to snap this face's vertices to the STL
        box.project_face(face_name, stl_name)
        print(f"  Projecting face '{face_name}' onto '{stl_name}'")

    mesh.add(box)
