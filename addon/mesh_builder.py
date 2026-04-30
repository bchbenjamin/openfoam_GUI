"""
addon/mesh_builder.py
Calls classy_blocks API to build blockMeshDict from a geometry spec dict.
No Blender imports — fully testable with plain Python/pytest.

SUPPORTED BLOCK TYPES:
  - box:     cb.Box(p_min, p_max)
  - cylinder: cb.Cylinder(axis_pt1, axis_pt2, radius_point)
  - sphere:  two cb.Hemisphere shapes
  - disk:    cb.FourCoreDisk(...) extruded by a thin amount
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


def _apply_round_chops(shape, spec: Dict[str, Any], axial_cells: int | None = None) -> None:
    """
    Applies chops to round shapes that expose radial/tangential/axial helpers.
    """
    grading_type = spec.get("grading_type", "RATIO")
    cells = spec["cells"]
    grading = spec.get("grading", [1.0, 1.0, 1.0])
    start_size = spec.get("start_size", 1e-4)
    end_size = spec.get("end_size", 1e-4)
    radial_cells = max(1, int(cells[0]))
    tangential_cells = max(1, int(cells[1]))
    axial_cells = max(1, int(axial_cells if axial_cells is not None else cells[2]))

    if grading_type == "START_SIZE":
        shape.chop_radial(count=radial_cells, start_size=start_size)
        shape.chop_tangential(count=tangential_cells, start_size=start_size)
        shape.chop_axial(count=axial_cells, start_size=start_size)
        return

    if grading_type == "SYMMETRIC":
        shape.chop_radial(start_size=start_size, end_size=end_size)
        shape.chop_tangential(start_size=start_size, end_size=end_size)
        shape.chop_axial(start_size=start_size, end_size=end_size)
        return

    shape.chop_radial(count=radial_cells, c2c_expansion=grading[0])
    shape.chop_tangential(count=tangential_cells, c2c_expansion=grading[1])
    shape.chop_axial(count=axial_cells, c2c_expansion=grading[2])


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
    Builds a Box block with optional terrain STL projection.

    Auto-detection now routes cylinders/spheres to their native cb classes,
    so this function no longer handles self-projection. It only handles
    user-specified single-face terrain projection.
    """
    print(f"[classy_blocks]   Building Box: p_min={spec['p_min']}, p_max={spec['p_max']}")
    box = cb.Box(spec["p_min"], spec["p_max"])
    _apply_chops(box, spec)

    # User-specified single-face terrain projection
    for face_name, terrain_stl in spec.get("stl_projections", {}).items():
        _register_geometry(mesh, terrain_stl)
        box.project_side(face_name, terrain_stl)
        print(f"[classy_blocks]   Terrain projection: '{face_name}' → '{terrain_stl}'")

    mesh.add(box)


def _build_cylinder(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds a Cylinder block using classy_blocks native cb.Cylinder.

    cb.Cylinder(axis_point_1, axis_point_2, radius_point_1):
      - axis_point_1, axis_point_2: endpoints of the cylinder central axis
      - radius_point_1: a point ON the cylinder surface at the start end

    cb.Cylinder generates a proper O-grid (12 hex blocks) — no STL projection
    needed. The output mesh is a true cylinder, not a projected bounding box.
    """
    axis_pt1 = spec["axis_pt1"]
    axis_pt2 = spec["axis_pt2"]
    radius_point = spec["radius_point"]
    radius = spec.get("radius", "?")
    print(f"[classy_blocks]   Building Cylinder: "
          f"axis=[{axis_pt1}→{axis_pt2}], radius={radius}")

    cyl = cb.Cylinder(axis_pt1, axis_pt2, radius_point)
    _apply_round_chops(cyl, spec)
    mesh.add(cyl)


def _build_sphere(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds a full sphere from two hemispheres.

    The split axis comes from the spec (derived from the object's world
    rotation). Falls back to [0,0,1] for backwards compatibility.
    """
    center = spec["center"]
    radius_point = spec["radius_point"]
    radius = spec.get("radius", "?")
    split = spec.get("split_axis", [0, 0, 1])
    neg_split = [-split[0], -split[1], -split[2]]
    print(f"[classy_blocks]   Building Sphere: center={center}, radius={radius}, "
          f"split_axis={[round(s,3) for s in split]}")

    upper = cb.Hemisphere(center, radius_point, split)
    lower = cb.Hemisphere(center, radius_point, neg_split)

    for hemi in (upper, lower):
        _apply_round_chops(hemi, spec, axial_cells=max(1, int(spec["cells"][2])))
        mesh.add(hemi)


def _build_disk(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds a thin structured disk for planar circle-like inputs.
    """
    center = spec["center"]
    radius_point = spec["radius_point"]
    normal = spec["normal"]
    thickness = spec["thickness"]
    vector = [float(component) * float(thickness) for component in normal]

    print(f"[classy_blocks]   Building Disk: center={center}, "
          f"thickness={thickness}, source={spec.get('source_kind')}")

    disk = cb.FourCoreDisk(center, radius_point, normal)
    shape = cb.ExtrudedShape(disk, vector)
    _apply_chops(shape, {
        **spec,
        "cells": [spec["cells"][0], spec["cells"][1], max(1, int(spec["cells"][2]))],
    })
    mesh.add(shape)


def _build_unsupported(_mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    print(f"[classy_blocks]   WARNING: skipping unsupported object "
          f"'{spec.get('name')}' ({spec.get('reason', 'unknown reason')})")


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

def build_block(mesh: cb.Mesh, spec: Dict[str, Any]) -> bool:
    """
    Dispatches block building by type.

    Supported types: box, cylinder, sphere, disk, extrude, revolve.
    """
    block_type = spec.get("type", "box")

    if block_type == "box":
        _build_box(mesh, spec)
        return True
    elif block_type == "cylinder":
        _build_cylinder(mesh, spec)
        return True
    elif block_type == "sphere":
        _build_sphere(mesh, spec)
        return True
    elif block_type == "disk":
        _build_disk(mesh, spec)
        return True
    elif block_type == "extrude":
        _build_extrude(mesh, spec)
        return True
    elif block_type == "revolve":
        _build_revolve(mesh, spec)
        return True
    elif block_type == "unsupported":
        _build_unsupported(mesh, spec)
        return False
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
    built_blocks = 0

    for block_spec in spec["blocks"]:
        block_name = block_spec.get("name", "unnamed")
        block_type = block_spec.get("type", "box")
        grading_type = block_spec.get("grading_type", "RATIO")
        print(f"[classy_blocks] Building {block_type} block: '{block_name}' "
              f"(grading: {grading_type})")
        if build_block(mesh, block_spec):
            built_blocks += 1

    if built_blocks == 0:
        raise ValueError("No supported blocks were available to write blockMeshDict")

    print(f"[classy_blocks] Writing blockMeshDict to: {output_path}")
    mesh.write(output_path)
    print(f"[classy_blocks] Written blockMeshDict: {output_path} "
          f"({os.path.getsize(output_path)} bytes)")
