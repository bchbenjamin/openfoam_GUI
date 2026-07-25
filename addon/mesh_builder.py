"""
Mesh Builder module.

Receives extracted parametric specifications and invokes the classy_blocks Python API
to construct conformal, structured blockMesh geometries.
"""

from __future__ import annotations
"""
addon/mesh_builder.py
Calls classy_blocks API to build blockMeshDict from a geometry spec dict.
No Blender imports — fully testable with plain Python/pytest.

SUPPORTED BLOCK TYPES:
  - box:      cb.Box(p_min, p_max)
  - cylinder: cb.Cylinder(axis_pt1, axis_pt2, radius_point)
  - frustum:  cb.Frustum(axis_pt1, axis_pt2, radius_pt1, radius_2)
  - sphere:   two cb.Hemisphere shapes
  - disk:     cb.FourCoreDisk(...) extruded by a thin amount
  - extrude:  cb.Extrude(cb.Face(4pts), vector)
  - revolve:  cb.Revolve(cb.Face(4pts), angle_rad, axis, origin)
  - loft:     cb.Loft(cb.Face(bottom), cb.Face(top))
  - wedge:    cb.Wedge(cb.Face(4pts), angle)

SHAPE CHAINING:
  - Cylinder.chain(source, length) — extend a pipe from another round shape
  - Frustum.chain(source, length, radius_2) — taper a pipe connection

TERRAIN PROJECTION (box only):
  - Single-face projection onto an STL surface via box.project_side()
  - Geometry registered via mesh.add_geometry() (list-of-strings format)

CRITICAL API NOTES:
  - _apply_face_patches(block, spec)
 mesh.add(block)       <- correct
  - mesh.merge(block)     <- does NOT exist
  - cb.Extrude(face, vec) <- face must be cb.Face, NOT a raw list
  - cb.Revolve(face, ...) <- same: face must be cb.Face
  - add_geometry signature: dict[str, list[str]]

CALLED BY: operators.py -> CLASSY_OT_generate_mesh.execute()
"""

import os
import math
try:
    import classy_blocks as cb
except ImportError:
    cb = None  # Handled gracefully by dependencies check
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
                       
    if "name" in spec:
        block.set_cell_zone(spec["name"])


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
    elif grading_type == "SYMMETRIC":
        shape.chop_radial(start_size=start_size, end_size=end_size)
        shape.chop_tangential(start_size=start_size, end_size=end_size)
        shape.chop_axial(start_size=start_size, end_size=end_size)
    else:
        shape.chop_radial(count=radial_cells, c2c_expansion=grading[0])
        shape.chop_tangential(count=tangential_cells, c2c_expansion=grading[1])
        shape.chop_axial(count=axial_cells, c2c_expansion=grading[2])
        
    if "name" in spec:
        if hasattr(shape, 'set_cell_zone'):
            shape.set_cell_zone(spec["name"])
        elif hasattr(shape, 'lofts'):
            for operation in shape.lofts:
                operation.set_cell_zone(spec["name"])



def _apply_face_patches(shape, spec):
    """Applies specific boundary conditions per face."""
    patches = spec.get("face_patches", [])
    for p in patches:
        side_name = p.get("side_name")
        patch_name = p.get("patch_name")
        if side_name and patch_name:
            try:
                shape.set_patch(patch_name, side_name)
            except Exception as e:
                pass


def _apply_stl_projections(shape, mesh_obj, spec):
    """
    Apply STL face projections to a shape using classy_blocks' native
    project_side() + add_geometry() mechanism.

    NATIVE VS FALLBACK:
        This uses OpenFOAM's searchableSurface (triSurfaceMesh) for projection,
        which is the preferred approach because blockMesh projects ALL mesh
        points on the face — not just control vertices. This respects mesh
        grading and curvature interpolation, producing much better terrain
        conformance than the Python-side pre-warping fallback in
        stl_projector.py.

    The 'stl_projections' key in the spec dict maps face names to STL
    filenames: {"top": "terrain.stl", "bottom": "ground.stl"}.

    Args:
        shape: The classy_blocks shape object (Box, Cylinder, Extrude, etc.).
        mesh_obj: The cb.Mesh object (needed for geometry registration).
        spec: Block specification dict.
    """
    if not hasattr(shape, "project_side"):
        return

    for face_name, terrain_stl in spec.get("stl_projections", {}).items():
        if not terrain_stl or not terrain_stl.strip():
            continue
        _register_geometry(mesh_obj, terrain_stl)
        shape.project_side(face_name, terrain_stl)


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
    pass


def _build_box(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds a Box block with optional terrain STL projection.

    Auto-detection now routes cylinders/spheres to their native cb classes,
    so this function no longer handles self-projection. It only handles
    user-specified single-face terrain projection.
    """
    pass
    box = cb.Box(spec["p_min"], spec["p_max"])
    _apply_chops(box, spec)
    if "matrix_world" in spec:
        box.transform(spec["matrix_world"])
    
    # STL face projection (native OpenFOAM searchableSurface mechanism)
    _apply_stl_projections(box, mesh, spec)
    
    _apply_face_patches(box, spec)
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
    pass

    cyl = cb.Cylinder(axis_pt1, axis_pt2, radius_point)
    _apply_round_chops(cyl, spec)
    if "matrix_world" in spec:
        cyl.transform(spec["matrix_world"])
    _apply_stl_projections(cyl, mesh, spec)
    _apply_face_patches(cyl, spec)
    mesh.add(cyl)
    return cyl



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
    pass
          
    shared_label = f"sphere_{spec.get('name', 'obj')}"
    
    class SharedHemisphere(cb.Hemisphere):
        @property
        def geometry_label(self):
            return shared_label

    upper = SharedHemisphere(center, radius_point, split)
    lower = SharedHemisphere(center, radius_point, neg_split)

    for hemi in (upper, lower):
        _apply_round_chops(hemi, spec, axial_cells=max(1, int(spec["cells"][2])))
        _apply_face_patches(hemi, spec)
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

    pass

    disk = cb.FourCoreDisk(center, radius_point, normal)
    shape = cb.ExtrudedShape(disk, vector)
    _apply_chops(shape, {
        **spec,
        "cells": [spec["cells"][0], spec["cells"][1], max(1, int(spec["cells"][2]))],
    })
    _apply_face_patches(shape, spec)
    mesh.add(shape)


def _build_unsupported(_mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    pass


def _build_extrude(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds an Extrude block from a quad face + extrusion vector.

    cb.Extrude(cb.Face(4pts), extrude_vector):
      face — a cb.Face wrapping 4 [x,y,z] points
      extrude_vector — [dx, dy, dz]
    """
    face_pts = spec["face"]
    vector = spec["extrude_vector"]
    pass

    face = cb.Face(face_pts)
    extrude = cb.Extrude(face, vector)
    _apply_chops(extrude, spec)
    if "matrix_world" in spec:
        extrude.transform(spec["matrix_world"])
    _apply_stl_projections(extrude, mesh, spec)
    _apply_face_patches(extrude, spec)
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
    pass

    face = cb.Face(face_pts)
    revolve = cb.Revolve(face, angle_rad, axis, origin)
    _apply_chops(revolve, spec)
    if "matrix_world" in spec:
        revolve.transform(spec["matrix_world"])
    _apply_stl_projections(revolve, mesh, spec)
    _apply_face_patches(revolve, spec)
    mesh.add(revolve)


def _build_frustum(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds a Frustum (truncated cone) block.

    cb.Frustum(axis_point_1, axis_point_2, radius_point_1, radius_2):
      - axis_point_1, axis_point_2: endpoints of the frustum axis
      - radius_point_1: a point ON the surface at axis_pt1 end
      - radius_2: scalar end radius (NOT a point!)
    """
    axis_pt1 = spec["axis_pt1"]
    axis_pt2 = spec["axis_pt2"]
    radius_point_1 = spec["radius_point_1"]
    radius_2 = spec["radius_2"]
    # Clamp radius_2 for pointy cones — cb.Frustum cannot handle zero radius
    radius_1 = spec.get("radius_1", 1.0)
    if radius_2 < 1e-6:
        radius_2 = max(radius_1 * 0.01, 1e-4)
        pass
    pass

    frustum = cb.Frustum(axis_pt1, axis_pt2, radius_point_1, radius_2)
    _apply_round_chops(frustum, spec)
    if "matrix_world" in spec:
        frustum.transform(spec["matrix_world"])
    _apply_stl_projections(frustum, mesh, spec)
    _apply_face_patches(frustum, spec)
    mesh.add(frustum)
    return frustum



def _build_loft(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds a Loft block connecting two quad faces (bottom → top).

    cb.Loft(bottom_face, top_face):
      Both faces must be cb.Face objects wrapping 4 [x,y,z] points.
    """
    bottom_pts = spec["bottom_face"]
    top_pts = spec["top_face"]
    pass

    bottom_face = cb.Face(bottom_pts)
    top_face = cb.Face(top_pts)
    loft = cb.Loft(bottom_face, top_face)
    _apply_chops(loft, spec)
    if "matrix_world" in spec:
        loft.transform(spec["matrix_world"])
    _apply_stl_projections(loft, mesh, spec)
    _apply_face_patches(loft, spec)
    mesh.add(loft)


def _build_wedge(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    """
    Builds a Wedge block for axisymmetric 2D cases.

    cb.Wedge(face, angle):
      - face: cb.Face wrapping 4 [x,y,z] points
      - angle: total wedge angle in radians (default ~2 degrees)

    The wedge revolves around the x-axis symmetrically by ±angle/2.
    Used for axisymmetric CFD (pipe flow, nozzles, etc.).
    """
    face_pts = spec["face"]
    angle_deg = spec.get("angle_deg", 2.0)
    angle_rad = math.radians(angle_deg)

    face = cb.Face(face_pts)
    # Wedge in classy_blocks revolves around x-axis.
    wedge = cb.Wedge(face, angle_rad)
    
    _apply_chops(wedge, spec)
    if "matrix_world" in spec:
        wedge.transform(spec["matrix_world"])
        
    if hasattr(wedge, "project_side"):
        _apply_stl_projections(wedge, mesh, spec)
        
    _apply_face_patches(wedge, spec)
    mesh.add(wedge)



# ─────────────────────── DISPATCHER ───────────────────────

def _build_extruded_ring(mesh: cb.Mesh, spec: Dict[str, Any]) -> None:
    axis_pt1 = spec["axis_pt1"]
    axis_pt2 = spec["axis_pt2"]
    outer_radius_pt = spec["outer_radius_pt"]
    inner_radius = spec["inner_radius"]
    pass
    ring = cb.ExtrudedRing(axis_pt1, axis_pt2, outer_radius_pt, inner_radius)
    _apply_round_chops(ring, spec)
    if "matrix_world" in spec:
        ring.transform(spec["matrix_world"])
    _apply_face_patches(ring, spec)
    mesh.add(ring)
    return ring

_BUILDERS = {
    "box":         _build_box,
    "cylinder":    _build_cylinder,
    "frustum":     _build_frustum,
    "sphere":      _build_sphere,
    "disk":        _build_disk,
    "extrude":     _build_extrude,
    "revolve":     _build_revolve,
    "loft":        _build_loft,
    "wedge":       _build_wedge,
    "unsupported": _build_unsupported,
    "extruded_ring": _build_extruded_ring,
}


def build_block(mesh: cb.Mesh, spec: Dict[str, Any]) -> bool:
    """
    Dispatches block building by type.

    Supported types: box, cylinder, frustum, sphere, disk, extrude,
                     revolve, loft, wedge.

    Returns True if a block was actually built, False if skipped.
    """
    block_type = spec.get("type", "box")
    builder = _BUILDERS.get(block_type)

    if builder is None:
        raise ValueError(
            f"Unknown block type '{block_type}' for block '{spec.get('name')}'"
        )

    try:
        result = builder(mesh, spec)
        # unsupported returns None without adding anything
        return block_type != "unsupported"
    except Exception as e:
        print(f"Warning: Failed to build block '{spec.get('name')}' ({block_type}): {e}")
        return False


# ─────────────────────── SHAPE CHAINING ───────────────────────


def _build_chained_block(mesh: cb.Mesh, spec: Dict[str, Any],
                         source_shape) -> bool:
    """
    Builds a block by chaining it from an existing round shape.

    Uses the .chain() classmethod on Cylinder/Frustum to extend a pipe
    from the end face of the source shape.

    Args:
        mesh: The cb.Mesh to add the shape to.
        spec: Block spec dict with chain_source, chain_length, chain_radius_2.
        source_shape: The classy_blocks shape object to chain from.

    Returns True if successfully chained.
    """
    chain_length = spec.get("chain_length", 1.0)
    chain_radius_2 = spec.get("chain_radius_2", 0.0)
    block_name = spec.get("name", "unnamed")

    try:
        if chain_radius_2 > 0:
            # Chain as a frustum (tapered connection)
            pass
            chained = cb.Frustum.chain(
                source_shape, chain_length, chain_radius_2
            )
        else:
            # Chain as a cylinder (same radius)
            pass
            chained = cb.Cylinder.chain(source_shape, chain_length)

        _apply_round_chops(chained, spec)
        _apply_face_patches(chained, spec)
        mesh.add(chained)
        return True

    except Exception as e:
        pass
        import traceback; traceback.print_exc()
        return False


# ─────────────────────── MAIN ENTRY POINT ───────────────────────

def build_from_spec(spec: Dict[str, Any], output_path: str) -> None:
    """
    Takes a geometry spec dict and writes a blockMeshDict to output_path.

    Two-pass strategy for shape chaining:
      Pass 1: Build all non-chained blocks, store their cb objects by name.
      Pass 2: Build chained blocks using their source's cb object.
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.isdir(output_dir):
        raise IOError(
            f"Output directory does not exist: {output_dir}\n"
            "Create it with: mkdir -p " + output_dir
        )

    mesh = cb.Mesh()
    built_blocks = 0

    # Separate chained vs non-chained blocks
    non_chained = []
    chained = []
    for block_spec in spec["blocks"]:
        if block_spec.get("chain_source"):
            chained.append(block_spec)
        else:
            non_chained.append(block_spec)

    # --- Pass 1: Build all non-chained blocks ---
    built_shapes = {}  # name -> classy_blocks shape object (for chaining)
    for block_spec in non_chained:
        block_name = block_spec.get("name", "unnamed")
        block_type = block_spec.get("type", "box")
        grading_type = block_spec.get("grading_type", "RATIO")
        pass

        # For round shapes, capture the returned object for chaining
        if block_type in ("cylinder", "frustum"):
            builder = _BUILDERS.get(block_type)
            if builder:
                result = builder(mesh, block_spec)
                if result is not None:
                    built_shapes[block_name] = result
                built_blocks += 1
        elif build_block(mesh, block_spec):
            built_blocks += 1

    # --- Pass 2: Build chained blocks ---
    for block_spec in chained:
        block_name = block_spec.get("name", "unnamed")
        source_name = block_spec["chain_source"]
        pass

        source_shape = built_shapes.get(source_name)
        if source_shape is None:
            pass
            continue

        if _build_chained_block(mesh, block_spec, source_shape):
            built_blocks += 1

    if built_blocks == 0:
        raise ValueError("No supported blocks were available to write blockMeshDict")

    pass
    mesh.write(output_path)
    pass
