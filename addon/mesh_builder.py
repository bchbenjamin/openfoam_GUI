"""
addon/mesh_builder.py
Calls classy_blocks API to build blockMeshDict from a geometry spec dict.
No Blender imports — fully testable with plain Python/pytest.

SUPPORTED BLOCK TYPES:
  - box:     cb.Box(p_min, p_max)
  - extrude: cb.Extrude(cb.Face(4pts), vector)
  - revolve: cb.Revolve(cb.Face(4pts), angle_rad, axis, origin)

TERRAIN PROJECTION (box only):
  - Single-face projection onto an STL surface via box.project_side()
  - Geometry registered via mesh.add_geometry() (list-of-strings format)

CRITICAL API NOTES:
  - mesh.add(block)       <- correct
  - mesh.merge(block)     <- does NOT exist
  - cb.Extrude(face, vec) <- face must be cb.Face, NOT a raw list
  - cb.Revolve(face, ...) <- same: face must be cb.Face
  - add_geometry signature: dict[str, list[str]]

CALLED BY: operators.py -> CLASSY_OT_generate_mesh.execute()
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
      - SYMMETRIC:   use start_size + end_size
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


def _register_geometry(mesh: cb.Mesh, stl_name: str) -> None:
    """
    Registers an STL geometry in the mesh's geometry section.

    This is REQUIRED for any face projection — without it, blockMesh
    will crash with "Cannot find surface ... in geometry".

    add_geometry signature: dict[str, list[str]]
    """
    mesh.add_geometry({
        stl_name: [
            'type triSurfaceMesh',
            f'file "{stl_name}"'
        ]
    })
    print(f"[classy_blocks]   Registered geometry: '{stl_name}'")


def _build_box(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds a Box block with optional STL projection.

    Two projection modes:
    1. SELF-PROJECTION (automatic): For non-box shapes (cylinders, cones, etc.),
       projects ALL 6 faces of the bounding box onto the object's own STL.
       This makes blockMesh snap vertices to the original shape's surface.
    2. TERRAIN PROJECTION (user-specified): Projects a single face onto a
       user-provided terrain STL file.
    """
    print(f"[classy_blocks]   Building Box: p_min={spec['p_min']}, p_max={spec['p_max']}")
    box = cb.Box(spec["p_min"], spec["p_max"])
    _apply_chops(box, spec)

    # Mode 1: Self-projection for complex shapes (auto-detected)
    needs_self = spec.get("needs_self_projection", False)
    stl_name = spec.get("self_stl_name", "")
    if needs_self and stl_name:
        _register_geometry(mesh, stl_name)
        all_faces = ["bottom", "top", "front", "back", "left", "right"]
        for face in all_faces:
            box.project_side(face, stl_name)
        print(f"[classy_blocks]   Self-projected ALL 6 faces onto '{stl_name}'")
    elif needs_self and not stl_name:
        raise ValueError(
            f"Block '{spec.get('name')}' needs self-projection but "
            "'self_stl_name' is not set — STL export failed in the operator."
        )

    # Mode 2: User-specified single-face terrain projection
    for face_name, terrain_stl in spec.get("stl_projections", {}).items():
        _register_geometry(mesh, terrain_stl)
        box.project_side(face_name, terrain_stl)
        print(f"[classy_blocks]   Terrain projection: '{face_name}' → '{terrain_stl}'")

    mesh.add(box)


def _build_extrude(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds an Extrude block from a quad face + extrusion vector.

    cb.Extrude(cb.Face(4pts), extrude_vector):
      face — a cb.Face wrapping 4 [x,y,z] points
      extrude_vector — [dx, dy, dz]
    """
    face_pts = spec["face"]
    vector = spec["extrude_vector"]
    print(f"[classy_blocks]   Building Extrude: face={face_pts[0]}..., vector={vector}")

    face = cb.Face(face_pts)
    extrude = cb.Extrude(face, vector)
    _apply_chops(extrude, spec)
    mesh.add(extrude)


def _build_revolve(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds a Revolve block from a quad face, angle, axis, and origin.

    cb.Revolve(cb.Face(4pts), angle_radians, axis_vector, origin_point):
      angle is in RADIANS — we convert from degrees here.
    """
    face_pts = spec["face"]
    angle_rad = math.radians(spec["angle_deg"])
    axis = spec["axis"]
    origin = spec["origin"]
    print(f"[classy_blocks]   Building Revolve: angle={spec['angle_deg']}°, "
          f"axis={axis}, origin={origin}")

    face = cb.Face(face_pts)
    revolve = cb.Revolve(face, angle_rad, axis, origin)
    _apply_chops(revolve, spec)
    mesh.add(revolve)


# ─────────────────────── DISPATCHER ───────────────────────

def build_block(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Dispatches block building by type.

    Supported types: box, extrude, revolve.
    """
    block_type = spec.get("type", "box")

    if block_type == "box":
        _build_box(mesh, spec)
    elif block_type == "extrude":
        _build_extrude(mesh, spec)
    elif block_type == "revolve":
        _build_revolve(mesh, spec)
    else:
        raise ValueError(
            f"Unknown block type '{block_type}' for block '{spec.get('name')}'"
        )


# ─────────────────────── MAIN ENTRY POINT ───────────────────────

def build_from_spec(spec: Dict[str, Any], output_path: str) -> None:
    """
    Takes a geometry spec dict and writes a blockMeshDict to output_path.
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.isdir(output_dir):
        raise IOError(
            f"Output directory does not exist: {output_dir}\n"
            "Create it with: mkdir -p " + output_dir
        )

    mesh = cb.Mesh()

    for block_spec in spec["blocks"]:
        block_name = block_spec.get("name", "unnamed")
        block_type = block_spec.get("type", "box")
        grading_type = block_spec.get("grading_type", "RATIO")
        print(f"[classy_blocks] Building {block_type} block: '{block_name}' "
              f"(grading: {grading_type})")
        build_block(mesh, block_spec)

    print(f"[classy_blocks] Writing blockMeshDict to: {output_path}")
    mesh.write(output_path)
    print(f"[classy_blocks] Written blockMeshDict: {output_path} "
          f"({os.path.getsize(output_path)} bytes)")
