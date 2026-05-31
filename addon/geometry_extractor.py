"""
addon/geometry_extractor.py
Reads Blender scene objects and builds a spec dict for mesh_builder.

TWO-LAYER TOPOLOGICAL AUTO-DETECTION PIPELINE:

  Layer 1 — Native Blender Heuristics (fast):
    Compares bounding-box volume to actual mesh volume.
      Ratio ≈ 1.00  → Box candidate
      Ratio ≈ 0.785 → Cylinder candidate (π/4)
      Ratio ≈ 0.524 → Sphere candidate (π/6)
      Otherwise      → Unsupported

  Layer 2 — PyVista Validation (accurate):
    Exports temp STL, loads via PyVista, checks:
      - is_manifold (watertight)
      - Unique normals count (boxes have ≤ 6 orthogonal directions)
      - Gaussian curvature (cylinders have K≈0 on side walls)

  This replaces the broken "universal blind STL projection" that caused
  OpenFOAM to crash with "Cannot find triSurface file".

SUPPORTED BLOCK TYPES (auto-detected):
  - box:         cb.Box(p_min, p_max)
  - cylinder:    cb.Cylinder(axis_pt1, axis_pt2, radius_point)
  - sphere:      two cb.Hemisphere shapes
  - disk:        thin structured disk for planar round profiles
  - unsupported: skipped with warning (future: snappyHexMesh pipeline)

MANUAL OVERRIDES (via panel):
  - EXTRUDE: cb.Extrude(cb.Face(4pts), vector)
  - REVOLVE: cb.Revolve(cb.Face(4pts), angle, axis, origin)

COORDINATE PRESERVATION:
  All coordinates are in absolute world space via obj.matrix_world.

CALLED BY: operators.py → CLASSY_OT_generate_mesh.execute()
"""

import os
import math
import tempfile
import numpy as np


def extract_geometry(context):
    """
    Main entry point. Iterates all mesh objects, dispatches by block_type.

    Returns:
        {
            "blocks": [ { spec dict per block } ],
            "merge_tolerance": 1e-4,
        }
    """
    blocks = []
    warnings = []

    for obj in context.scene.objects:
        if obj.type != 'MESH':
            continue

        props = getattr(obj, "classy_block_props", None)

        # Exclude check
        if props and getattr(props, "exclude_from_mesh", False):
            print(f"[classy_blocks] Skipping '{obj.name}' (excluded)")
            continue

        # Check for unapplied transforms (warn only, never auto-apply)
        transform_warning = _check_unapplied_transforms(obj)
        if transform_warning:
            warnings.append(transform_warning)
            print(f"[classy_blocks]   WARNING: {transform_warning}")

        block_type = getattr(props, "block_type", "BOX") if props else "BOX"

        try:
            if block_type == "EXTRUDE":
                spec = _extract_extrude(obj, props)
            elif block_type == "REVOLVE":
                spec = _extract_revolve(obj, props)
            else:
                # BOX is the default — but we now auto-detect the actual shape
                spec = _extract_auto_detected(obj, props)

            blocks.append(spec)
            if spec["type"] == "unsupported":
                warnings.append(spec["warning"])
            else:
                print(f"[classy_blocks] Extracted '{spec['type']}' block: "
                      f"'{obj.name}'")

        except Exception as e:
            print(f"[classy_blocks] ERROR extracting '{obj.name}': {e}")
            import traceback; traceback.print_exc()
            continue

    print(f"[classy_blocks] Total blocks extracted: {len(blocks)}")
    return {
        "blocks": blocks,
        "merge_tolerance": 1e-4,
        "warnings": warnings,
    }


# ─────────────────────── AUTO-DETECTION ───────────────────────


def _extract_auto_detected(obj, props):
    """
    Two-Layer Topological Auto-Detection.

    Layer 1: Volume ratio heuristic (fast, from Blender data).
    Layer 2: PyVista validation (accurate, from exported mesh).

    Returns a typed spec dict, including non-blocking 'unsupported' specs.
    """
    # NOTE: Planar shapes (circles, disks) are NOT supported as structured meshes.
    # OpenFOAM requires 3D volume domains. The zero-thickness guard below will
    # catch these and flag as unsupported with an actionable message.

    # --- Layer 1: Volume Ratio Heuristic ---
    p_min, p_max = _get_world_bounding_box(obj)
    bb_dims = [p_max[i] - p_min[i] for i in range(3)]

    # Guard against zero-dimension objects (planes, lines)
    if any(d < 1e-8 for d in bb_dims):
        print(f"[classy_blocks]   '{obj.name}': zero-thickness dimension "
              f"({bb_dims}) — treating as unsupported")
        return _make_unsupported_spec(obj, props, "zero-thickness")

    bb_volume = bb_dims[0] * bb_dims[1] * bb_dims[2]

    # Get actual mesh volume
    mesh_volume = _compute_mesh_volume(obj)
    if mesh_volume is None or mesh_volume < 1e-12:
        print(f"[classy_blocks]   '{obj.name}': cannot compute mesh volume "
              f"— treating as unsupported")
        return _make_unsupported_spec(obj, props, "no-volume")

    ratio = mesh_volume / bb_volume
    print(f"[classy_blocks]   '{obj.name}': volume ratio = {ratio:.4f} "
          f"(mesh={mesh_volume:.6f}, bbox={bb_volume:.6f})")

    # Classify by ratio
    BOX_RATIO = 1.0
    CYL_RATIO = math.pi / 4      # ≈ 0.7854
    SPH_RATIO = math.pi / 6      # ≈ 0.5236
    TOLERANCE = 0.12              # ±12% tolerance for heuristic match

    candidate = "unsupported"
    if abs(ratio - BOX_RATIO) < TOLERANCE:
        candidate = "box"
    elif abs(ratio - CYL_RATIO) < TOLERANCE:
        candidate = "cylinder"
    elif abs(ratio - SPH_RATIO) < TOLERANCE:
        candidate = "sphere"

    print(f"[classy_blocks]   Layer 1 candidate: '{candidate}'")

    # --- Layer 2: PyVista Validation ---
    validated = _validate_with_pyvista(obj, candidate)
    if validated != candidate:
        print(f"[classy_blocks]   Layer 2 override: '{candidate}' → "
              f"'{validated}'")

    # --- Build typed spec ---
    if validated == "box":
        return _build_box_spec(obj, props, p_min, p_max)
    elif validated == "cylinder":
        return _build_cylinder_spec(obj, props, p_min, p_max, bb_dims)
    elif validated == "sphere":
        return _build_sphere_spec(obj, props, p_min, p_max)
    else:
        return _make_unsupported_spec(obj, props, validated)


def _extract_planar_round_shape(obj, props):
    """
    Detect supported planar round profiles (filled disks and circle outlines).

    OpenFOAM still needs a 3D volume mesh, so circle-like meshes are turned into
    thin structured disks instead of being silently dropped.
    """
    mesh_data = _get_world_mesh_data(obj)
    if mesh_data is None:
        return None

    points, faces = mesh_data
    if len(points) < 3:
        return None

    center = np.mean(points, axis=0)
    centered = points - center

    try:
        _, singular_values, vh = np.linalg.svd(centered, full_matrices=False)
    except np.linalg.LinAlgError:
        return None

    if len(singular_values) < 3:
        return None

    dominant = max(float(singular_values[0]), 1e-12)
    if float(singular_values[-1]) / dominant > 1e-4:
        return None

    axis_u = vh[0]
    axis_v = vh[1]
    normal = vh[2]

    u_coords = centered @ axis_u
    v_coords = centered @ axis_v
    plane_dims = [
        float(np.max(u_coords) - np.min(u_coords)),
        float(np.max(v_coords) - np.min(v_coords)),
    ]

    if min(plane_dims) < 1e-8:
        return None

    aspect_ratio = max(plane_dims) / max(min(plane_dims), 1e-12)
    if aspect_ratio > 1.15:
        return _make_unsupported_spec(obj, props, "planar-non-round")

    radii = np.sqrt(u_coords**2 + v_coords**2)
    mean_radius = float(np.mean(radii))
    if mean_radius < 1e-8:
        return _make_unsupported_spec(obj, props, "planar-degenerate")

    radial_variation = float(np.std(radii) / mean_radius)
    area_ratio = None
    if faces:
        bbox_area = plane_dims[0] * plane_dims[1]
        if bbox_area > 1e-12:
            area_ratio = _compute_polygon_area(points, faces) / bbox_area

    is_filled_disk = area_ratio is not None and abs(area_ratio - (math.pi / 4.0)) < 0.18
    is_circle_outline = len(points) >= 8 and radial_variation < 0.08

    if not (is_filled_disk or is_circle_outline):
        return None

    radius = 0.25 * (plane_dims[0] + plane_dims[1])
    thickness = max(max(plane_dims) * 0.01, 1e-4)
    normal = _normalize_vector(normal)
    center = center.tolist()
    radius_point = (np.asarray(center) + axis_u * radius).tolist()

    print(f"[classy_blocks]   '{obj.name}': planar round profile detected "
          f"— CFD domains must be 3D. Extrude this shape in Blender.")
    return _make_unsupported_spec(
        obj, props,
        "planar-2D (CFD domains must be 3D — extrude this shape before meshing)"
    )


def _compute_mesh_volume(obj):
    """
    Compute the actual volume of a Blender mesh object.
    Uses bmesh for accurate signed volume calculation.
    """
    import bpy
    import bmesh

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)

    bm = bmesh.new()
    bm.from_mesh(obj_eval.data)
    bm.transform(obj.matrix_world)
    volume = bm.calc_volume()
    bm.free()

    return abs(volume)


def _validate_with_pyvista(obj, candidate):
    """
    Layer 2: Validate the candidate classification using PyVista.

    - For boxes: check unique normal directions (should be ≤ 6)
    - For cylinders: check Gaussian curvature (side walls K ≈ 0)
    - For all: check manifold (watertight)

    Returns the validated type string.
    """
    try:
        import pyvista as pv
        import bpy

        # Export to temp STL for PyVista analysis
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as tmp:
            tmp_path = tmp.name

        # Export using Blender
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.wm.stl_export(filepath=tmp_path, export_selected_objects=True)

        pv_mesh = pv.read(tmp_path)
        os.unlink(tmp_path)

        # Check manifold (watertight)
        surface = pv_mesh.extract_surface()
        is_manifold = surface.is_manifold
        if not is_manifold:
            print(f"[classy_blocks]   PyVista: NOT manifold — downgrading")
            return "unsupported"

        if candidate == "box":
            return _validate_box_pyvista(surface)
        elif candidate == "cylinder":
            return _validate_cylinder_pyvista(surface)
        elif candidate == "sphere":
            return _validate_sphere_pyvista(surface)
        else:
            return candidate

    except ImportError:
        print(f"[classy_blocks]   PyVista not available — using Layer 1 only")
        return candidate
    except Exception as e:
        print(f"[classy_blocks]   PyVista validation error: {e}")
        return candidate


def _validate_box_pyvista(surface):
    """
    Validate a box candidate: check that face normals point in ≤ 6
    orthogonal directions.
    """
    normals = np.array(surface.face_normals)
    if len(normals) == 0:
        return "unsupported"

    # Round normals to snap to axis-aligned directions
    rounded = np.round(normals, decimals=1)
    unique = np.unique(rounded, axis=0)

    if len(unique) <= 6:
        print(f"[classy_blocks]   PyVista: {len(unique)} unique normals — "
              f"confirmed BOX")
        return "box"
    else:
        print(f"[classy_blocks]   PyVista: {len(unique)} unique normals — "
              f"NOT a box")
        return "unsupported"


def _validate_cylinder_pyvista(surface):
    """
    Validate a cylinder candidate: check that the mesh has both flat caps
    (normals along one axis) and curved sides.
    """
    normals = np.array(surface.face_normals)
    if len(normals) == 0:
        return "unsupported"

    # For a cylinder aligned along an axis, the cap faces have normals
    # pointing purely along that axis. The side faces have normals that
    # are perpendicular to that axis.

    # Find which axis has the most "pure" normals (cap faces)
    for axis_idx in range(3):
        axis_normals = np.abs(normals[:, axis_idx])
        cap_mask = axis_normals > 0.9  # Faces pointing along this axis
        cap_count = np.sum(cap_mask)

        if cap_count >= 2:  # At least 2 cap faces
            side_mask = ~cap_mask
            side_count = np.sum(side_mask)
            if side_count > 0:
                # Side normals should have zero component along the cylinder axis
                side_axis_component = np.abs(normals[side_mask, axis_idx])
                mean_axis = np.mean(side_axis_component)
                if mean_axis < 0.15:
                    print(f"[classy_blocks]   PyVista: {cap_count} cap faces, "
                          f"{side_count} side faces along axis {axis_idx} — "
                          f"confirmed CYLINDER")
                    return "cylinder"

    print(f"[classy_blocks]   PyVista: no clear cylinder axis found")
    return "unsupported"


def _validate_sphere_pyvista(surface):
    """
    Validate a sphere candidate by checking isotropic bounds after manifold
    validation has already passed.
    """
    bounds = surface.bounds
    dims = [
        float(bounds[1] - bounds[0]),
        float(bounds[3] - bounds[2]),
        float(bounds[5] - bounds[4]),
    ]

    if min(dims) < 1e-8:
        return "unsupported"

    aspect_ratio = max(dims) / min(dims)
    if aspect_ratio <= 1.12:
        print(f"[classy_blocks]   PyVista: isotropic bounds — confirmed SPHERE")
        return "sphere"

    print(f"[classy_blocks]   PyVista: anisotropic bounds ({dims}) — NOT a sphere")
    return "unsupported"


# ─────────────────────── SPEC BUILDERS ───────────────────────


def _build_box_spec(obj, props, p_min, p_max):
    """Build a spec dict for a confirmed box shape."""
    spec = {
        "type": "box",
        "name": obj.name,
        "p_min": p_min,
        "p_max": p_max,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
    }

    # Optional user-specified terrain STL projection
    if props:
        stl_file = getattr(props, "stl_file", "") or ""
        # Blender's FILE_PATH subtype may return "//" (blend-relative prefix)
        # even when the user never set a file. Strip it and check for a real name.
        stl_basename = os.path.basename(stl_file.strip())
        if stl_basename:
            face_name = getattr(props, "stl_projection_face", "top")
            spec["stl_projections"] = {
                face_name: stl_basename
            }
            print(f"[classy_blocks]   User STL projection: "
                  f"'{face_name}' → '{stl_basename}'")

    return spec


def _build_cylinder_spec(obj, props, p_min, p_max, bb_dims):
    """
    Build a spec dict for a confirmed cylinder shape.

    cb.Cylinder(axis_pt1, axis_pt2, radius_point):
      - axis_pt1, axis_pt2: endpoints of the cylinder axis
      - radius_point: a point ON the cylinder surface at the same Z as axis_pt1

    We detect the cylinder axis as the longest bounding box dimension,
    then compute the radius from the shorter two dimensions.
    """
    from mathutils import Vector

    local_vertices, face_normals, face_areas = _get_local_mesh_geometry(obj)
    if len(local_vertices) == 0:
        local_vertices = np.array([list(corner) for corner in obj.bound_box], dtype=float)
        face_normals = None
        face_areas = None

    pt1_local, pt2_local, rad_pt_local, radius_local = _infer_cylinder_local_frame(
        local_vertices,
        face_normals,
        face_areas,
    )

    # Transform to absolute world space
    mat = obj.matrix_world
    axis_pt1 = list(mat @ Vector(pt1_local))
    axis_pt2 = list(mat @ Vector(pt2_local))
    radius_point = list(mat @ Vector(rad_pt_local))
    radius = float(np.linalg.norm(np.asarray(radius_point) - np.asarray(axis_pt1)))

    print(f"[classy_blocks]   Cylinder: local_radius={radius_local:.4f}, "
          f"world_radius={radius:.4f}, axis_start="
          f"[{axis_pt1[0]:.2f}, {axis_pt1[1]:.2f}, {axis_pt1[2]:.2f}] → ...")

    return {
        "type": "cylinder",
        "name": obj.name,
        "axis_pt1": axis_pt1,
        "axis_pt2": axis_pt2,
        "radius_point": radius_point,
        "radius": radius,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
    }


def _build_sphere_spec(obj, props, p_min, p_max):
    """
    Build a spec dict for a confirmed sphere shape.

    classy_blocks does not expose a single full-sphere constructor, so the
    builder will create two hemispheres around the same center.

    The split axis is derived from the object's world rotation so that
    rotated spheres are split along their actual local Z, not hard-coded [0,0,1].
    """
    from mathutils import Vector

    center = [
        (p_min[0] + p_max[0]) / 2.0,
        (p_min[1] + p_max[1]) / 2.0,
        (p_min[2] + p_max[2]) / 2.0,
    ]
    radius = sum((p_max[i] - p_min[i]) / 2.0 for i in range(3)) / 3.0
    radius_point = [center[0] + radius, center[1], center[2]]

    # Compute split axis: transform local Z by the object's world rotation
    rot_matrix = obj.matrix_world.to_3x3()
    split_axis = list((rot_matrix @ Vector((0, 0, 1))).normalized())

    return {
        "type": "sphere",
        "name": obj.name,
        "center": center,
        "radius_point": radius_point,
        "radius": radius,
        "split_axis": split_axis,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
    }


def _make_unsupported_spec(obj, props, reason):
    """
    Handle unsupported shapes: print a loud warning and return None.

    Future: these objects will be routed to the snappyHexMesh pipeline.
    """
    warning = (f"{obj.name}: unsupported mesh ({reason}) — it will stay in the "
               "Blender scene but be skipped during blockMesh generation.")
    print("")
    print("  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  UNSUPPORTED SHAPE: '{obj.name}'")
    print(f"  ║  Reason: {reason}")
    print("  ║  This object will be SKIPPED from the mesh.")
    print("  ║  Future: snappyHexMesh pipeline for complex shapes.")
    print("  ╚══════════════════════════════════════════════════════╝")
    print("")
    return {
        "type": "unsupported",
        "name": obj.name,
        "reason": reason,
        "warning": warning,
        "patch_name": _read_patch_name(props),
    }


# ─────────────────────── MANUAL EXTRACTORS ───────────────────────


def _extract_extrude(obj, props):
    """
    EXTRUDE: extract a quad face from the object and an extrusion vector.
    """
    face_index = getattr(props, "extrude_face_index", 0) if props else 0
    face_verts = _extract_face_vertices_world(obj, face_index)

    if len(face_verts) != 4:
        raise ValueError(
            f"Extrude face {face_index} on '{obj.name}' has "
            f"{len(face_verts)} vertices — must be exactly 4 (a quad)."
        )

    extrude_axis_name = getattr(props, "extrude_axis", "Z") if props else "Z"
    distance = getattr(props, "extrude_distance", 1.0) if props else 1.0

    axis_map = {"X": [1, 0, 0], "Y": [0, 1, 0], "Z": [0, 0, 1]}
    axis_vec = axis_map.get(extrude_axis_name, [0, 0, 1])
    extrude_vector = [v * distance for v in axis_vec]

    return {
        "type": "extrude",
        "name": obj.name,
        "face": face_verts,
        "extrude_vector": extrude_vector,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
    }


def _extract_revolve(obj, props):
    """
    REVOLVE: extract a quad face and revolve parameters.
    """
    face_index = getattr(props, "revolve_face_index", 0) if props else 0
    face_verts = _extract_face_vertices_world(obj, face_index)

    if len(face_verts) != 4:
        raise ValueError(
            f"Revolve face {face_index} on '{obj.name}' has "
            f"{len(face_verts)} vertices — must be exactly 4."
        )

    angle_deg = getattr(props, "revolve_angle", 90.0) if props else 90.0
    axis_name = getattr(props, "revolve_axis", "Z") if props else "Z"
    origin = list(getattr(props, "revolve_origin", (0, 0, 0))) if props else [0, 0, 0]

    axis_map = {"X": [1, 0, 0], "Y": [0, 1, 0], "Z": [0, 0, 1]}
    axis_vec = axis_map[axis_name]

    return {
        "type": "revolve",
        "name": obj.name,
        "face": face_verts,
        "angle_deg": angle_deg,
        "axis": axis_vec,
        "origin": origin,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
    }


# ─────────────────────── HELPERS ───────────────────────


def _get_world_bounding_box(obj):
    """
    Returns (p_min, p_max) for a Blender object in absolute world space.

    CRITICAL: obj.bound_box returns bpy_prop_array items, NOT Vector objects.
    Must wrap each corner in mathutils.Vector() before matrix multiplication.
    """
    from mathutils import Vector

    world_corners = []
    for corner in obj.bound_box:
        local_vec = Vector(corner)
        world_co = obj.matrix_world @ local_vec
        world_corners.append(world_co)

    xs = [c[0] for c in world_corners]
    ys = [c[1] for c in world_corners]
    zs = [c[2] for c in world_corners]

    p_min = [min(xs), min(ys), min(zs)]
    p_max = [max(xs), max(ys), max(zs)]

    return p_min, p_max


def _extract_face_vertices_world(obj, face_index):
    """
    Returns a list of [x, y, z] world-space coordinates for a face's vertices.
    """
    import bpy
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data

    if face_index >= len(mesh.polygons):
        raise IndexError(
            f"Face index {face_index} out of range — object '{obj.name}' "
            f"has only {len(mesh.polygons)} faces."
        )

    poly = mesh.polygons[face_index]
    verts_world = []
    for vi in poly.vertices:
        co_local = mesh.vertices[vi].co
        co_world = obj.matrix_world @ co_local
        verts_world.append([co_world.x, co_world.y, co_world.z])

    return verts_world


def _get_world_mesh_data(obj):
    """
    Returns evaluated mesh vertices in world coordinates plus polygon indices.
    """
    import bpy

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data

    if not hasattr(mesh, "vertices"):
        return None

    world_points = np.array(
        [list(obj_eval.matrix_world @ v.co) for v in mesh.vertices],
        dtype=float,
    )
    faces = [list(poly.vertices) for poly in getattr(mesh, "polygons", [])]
    return world_points, faces


def _get_local_mesh_geometry(obj):
    """
    Returns evaluated mesh vertices in local coordinates and face normal/area data.
    """
    import bpy

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data

    vertices = np.array([list(v.co) for v in mesh.vertices], dtype=float)
    face_normals = np.array([list(poly.normal) for poly in mesh.polygons], dtype=float)
    face_areas = np.array([float(poly.area) for poly in mesh.polygons], dtype=float)
    return vertices, face_normals, face_areas


def _infer_cylinder_local_frame(vertices, face_normals=None, face_areas=None):
    """
    Infer cylinder endpoints and radius point in local space.

    This avoids relying on bounding-box ties like Blender's default cylinder
    where diameter and height can both be 2 units.
    """
    points = np.asarray(vertices, dtype=float)
    if len(points) == 0:
        raise ValueError("Cylinder inference needs at least one vertex")

    axis_dir = _infer_axis_from_opposite_normals(face_normals, face_areas)
    if axis_dir is None:
        dims = np.max(points, axis=0) - np.min(points, axis=0)
        axis_dir = np.zeros(3, dtype=float)
        axis_dir[int(np.argmax(dims))] = 1.0

    axis_dir = np.asarray(_normalize_vector(axis_dir), dtype=float)
    center = np.mean(points, axis=0)
    centered = points - center
    projections = centered @ axis_dir
    pt1 = center + axis_dir * float(np.min(projections))
    pt2 = center + axis_dir * float(np.max(projections))

    radial_vectors = centered - np.outer(projections, axis_dir)
    radial_lengths = np.linalg.norm(radial_vectors, axis=1)
    radius = float(np.max(radial_lengths))

    if radius < 1e-8:
        raise ValueError("Cylinder inference produced zero radius")

    radius_index = int(np.argmax(radial_lengths))
    radius_dir = radial_vectors[radius_index] / radial_lengths[radius_index]
    radius_point = pt1 + radius_dir * radius

    return pt1.tolist(), pt2.tolist(), radius_point.tolist(), radius


def _infer_axis_from_opposite_normals(face_normals, face_areas):
    """
    Finds the dominant axis from the largest opposite normal pair.
    """
    if face_normals is None or face_areas is None:
        return None

    normals = np.asarray(face_normals, dtype=float)
    areas = np.asarray(face_areas, dtype=float)
    if len(normals) == 0 or len(areas) != len(normals):
        return None

    unit_normals = []
    for normal in normals:
        norm = np.linalg.norm(normal)
        if norm < 1e-8:
            unit_normals.append(None)
        else:
            unit_normals.append(normal / norm)

    best_axis = None
    best_score = -1.0
    for i in range(len(unit_normals)):
        ni = unit_normals[i]
        if ni is None:
            continue
        for j in range(i + 1, len(unit_normals)):
            nj = unit_normals[j]
            if nj is None:
                continue
            if float(np.dot(ni, nj)) >= -0.98:
                continue

            score = float(areas[i] + areas[j])
            if score > best_score:
                best_score = score
                best_axis = ni

    return best_axis


def _compute_polygon_area(points, faces):
    """
    Computes total polygon area from world-space vertices and polygon indices.
    """
    total_area = 0.0
    for face in faces:
        if len(face) < 3:
            continue
        p0 = points[face[0]]
        for i in range(1, len(face) - 1):
            p1 = points[face[i]]
            p2 = points[face[i + 1]]
            total_area += 0.5 * np.linalg.norm(np.cross(p1 - p0, p2 - p0))
    return float(total_area)


def _normalize_vector(vector):
    vec = np.asarray(vector, dtype=float)
    norm = float(np.linalg.norm(vec))
    if norm < 1e-12:
        return [0.0, 0.0, 1.0]
    return (vec / norm).tolist()


def _read_cells(props):
    raw = getattr(props, "cells", None) if props else None
    if raw and len(raw) >= 3:
        return [max(1, int(raw[i])) for i in range(3)]
    return [10, 10, 10]


def _read_patch_name(props):
    return getattr(props, "patch_name", "defaultWall") if props else "defaultWall"


def _read_grading(props):
    gt = getattr(props, "grading_type", "RATIO") if props else "RATIO"
    raw_g = getattr(props, "grading", None) if props else None
    grading = [float(raw_g[i]) for i in range(3)] if raw_g and len(raw_g) >= 3 else [1.0, 1.0, 1.0]
    return {
        "grading_type": gt,
        "grading": grading,
        "start_size": float(getattr(props, "start_size", 1e-4) if props else 1e-4),
        "end_size": float(getattr(props, "end_size", 1e-4) if props else 1e-4),
    }


def _check_unapplied_transforms(obj):
    """
    Checks if an object has unapplied scale.

    Returns a warning string if scale != (1,1,1), else None.
    The pipeline still works correctly (we use matrix_world for all coords),
    but unapplied scale can cause confusion if the user is thinking in local
    coordinates. We warn — we NEVER auto-apply (that would break modifiers,
    constraints, and animations).
    """
    scale = obj.scale
    threshold = 1e-4
    has_unapplied_scale = (
        abs(scale[0] - 1.0) > threshold or
        abs(scale[1] - 1.0) > threshold or
        abs(scale[2] - 1.0) > threshold
    )
    if has_unapplied_scale:
        return (f"'{obj.name}' has unapplied scale "
                f"({scale[0]:.2f}, {scale[1]:.2f}, {scale[2]:.2f}). "
                f"Apply scale (Ctrl+A) for predictable results.")
    return None
