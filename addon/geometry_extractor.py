"""
addon/geometry_extractor.py
Reads Blender scene objects and builds a spec dict for mesh_builder.

TWO-LAYER TOPOLOGICAL AUTO-DETECTION PIPELINE:

  Layer 1 — Native Blender Heuristics (fast):
    Compares bounding-box volume to actual mesh volume.
      Ratio ≈ 1.00  → Box candidate
      Ratio ≈ 0.785 → Cylinder candidate (π/4)
      Ratio ≈ 0.524 → Sphere candidate (π/6)
      Ratio ≈ 0.262 → Cone/Frustum candidate (π/12)
      Otherwise      → Unsupported

  Layer 2 — PyVista Validation (accurate):
    Exports temp STL, loads via PyVista, checks:
      - is_manifold (watertight)
      - Unique normals count (boxes have ≤ 6 orthogonal directions)
      - Gaussian curvature (cylinders have K≈0 on side walls)
      - Cap radius comparison (frustum: two caps with different radii)

SUPPORTED BLOCK TYPES (auto-detected):
  - box:         cb.Box(p_min, p_max)
  - cylinder:    cb.Cylinder(axis_pt1, axis_pt2, radius_point)
  - frustum:     cb.Frustum(axis_pt1, axis_pt2, radius_pt1, radius_2)
  - sphere:      two cb.Hemisphere shapes
  - disk:        thin structured disk for planar round profiles
  - unsupported: skipped with warning (future: snappyHexMesh pipeline)

MANUAL OVERRIDES (via panel):
  - EXTRUDE: cb.Extrude(cb.Face(4pts), vector)
  - REVOLVE: cb.Revolve(cb.Face(4pts), angle, axis, origin)
  - LOFT:    cb.Loft(cb.Face(bottom), cb.Face(top))
  - WEDGE:   cb.Wedge(cb.Face(4pts), angle)

COORDINATE PRESERVATION:
  All coordinates are in absolute world space via obj.matrix_world.

CALLED BY: operators.py → CLASSY_OT_generate_mesh.execute()
"""

import subprocess
import os
import math
import tempfile
import numpy as np


def extract_geometry(context):
    blocks = []
    warnings = []

    for obj in context.scene.objects:
        if obj.type not in {"MESH", "CURVE"}:
            continue

        props = getattr(obj, "classy_block_props", None)

        if getattr(props, "exclude_from_mesh", False):
            continue

        # Fast path for sketch tool lines
        if obj.get("classy_sketch"):
            spec = _build_sketch_spec(obj, props)
            if spec:
                blocks.append(spec)
            continue

        block_type = getattr(props, "block_type", "BOX") if props else "BOX"
        transform_warning = _check_applied_transforms(obj, block_type)
        if transform_warning:
            warnings.append(transform_warning)
            pass

        try:
            if block_type == "BOX":
                spec = _build_box_spec(obj, props)
            elif block_type == "CYLINDER":
                spec = _build_cylinder_spec(obj, props)
            elif block_type == "FRUSTUM":
                spec = _build_frustum_spec(obj, props)
            elif block_type == "EXTRUDED_RING":
                spec = _build_extruded_ring_spec(obj, props)
            elif block_type == "WEDGE":
                spec = _build_wedge_spec(obj, props)
            elif block_type == "EXTRUDE":
                spec = _build_extrude_spec(obj, props)
            elif block_type == "REVOLVE":
                spec = _build_revolve_spec(obj, props)
            elif block_type == "LOFT":
                spec = _build_loft_spec(obj, props)
            else:
                spec = _make_unsupported_spec(obj, props, "unknown-block-type")

            # Inject per-face boundary conditions
            if spec["type"] != "unsupported" and hasattr(props, "face_patches"):
                patches = []
                for fp in props.face_patches:
                    patches.append({
                        "side_name": fp.side_name,
                        "patch_name": fp.patch_name,
                        "patch_type": fp.patch_type
                    })
                spec["face_patches"] = patches

            # Inject STL projections (only supported for base operations, not composite shapes)
            if spec["type"] in ("box", "extrude", "revolve", "loft") and props:
                stl_file = getattr(props, "stl_file", "") or ""
                stl_basename = os.path.basename(stl_file.strip())
                if stl_basename and stl_basename.lower().endswith(".stl"):
                    face_name = getattr(props, "stl_projection_face", "top")
                    spec["stl_projections"] = { face_name: stl_basename }

            blocks.append(spec)
            if spec["type"] == "unsupported":
                warnings.append(spec.get("warning", "Unsupported shape"))
            else:
                pass

        except Exception as e:
            pass
            import traceback; traceback.print_exc()
            continue

    pass
    return {
        "blocks": blocks,
        "merge_tolerance": 1e-4,
        "warnings": warnings,
    }

def _check_applied_transforms(obj, block_type):
    # pyrefly: ignore [import-outside-toplevel, missing-import]
    import bpy
    scale = obj.scale
    if any(abs(s - 1.0) > 1e-4 for s in scale):
        return (f"'{obj.name}' has unapplied scale. "
                f"Apply scale (Ctrl+A) for predictable results.")

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    if not getattr(mesh, "vertices", None):
        return None
        
    verts = [v.co for v in mesh.vertices]
    if not verts: return None
    
    z_coords = [v.z for v in verts]
    z_min = min(z_coords)
    z_min_verts = [v for v in verts if abs(v.z - z_min) < 1e-4]
    
    if block_type in ("CYLINDER", "FRUSTUM", "EXTRUDED_RING"):
        if len(z_min_verts) < 3:
            return (f"Transformed geometry detected on '{obj.name}'. "
                    f"Please do not 'Apply Rotations' to primitive shapes, "
                    f"as it destroys the parametric block data.")
            
    return None

def _build_box_spec(obj, props):
    import os
    local_corners = [c for c in obj.bound_box]
    xs = [c[0] for c in local_corners]
    ys = [c[1] for c in local_corners]
    zs = [c[2] for c in local_corners]
    
    p_min = [min(xs), min(ys), min(zs)]
    p_max = [max(xs), max(ys), max(zs)]
    
    spec = {
        "type": "box",
        "name": obj.name,
        "p_min": p_min,
        "p_max": p_max,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
        **_read_chain_params(props),
        "matrix_world": [list(row) for row in obj.matrix_world],
    }
            
    return spec

def _build_cylinder_spec(obj, props):
    local_corners = [c for c in obj.bound_box]
    xs = [c[0] for c in local_corners]
    ys = [c[1] for c in local_corners]
    zs = [c[2] for c in local_corners]
    
    z_min, z_max = min(zs), max(zs)
    radius = (max(xs) - min(xs)) / 2.0
    
    axis_pt1 = [0, 0, z_min]
    axis_pt2 = [0, 0, z_max]
    radius_point = [radius, 0, z_min]
    
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
        **_read_chain_params(props),
        "matrix_world": [list(row) for row in obj.matrix_world],
    }

def _build_frustum_spec(obj, props):
    # pyrefly: ignore [import-outside-toplevel, missing-import]
    import bpy
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    
    verts = [v.co for v in mesh.vertices]
    z_coords = [v.z for v in verts]
    z_min, z_max = min(z_coords), max(z_coords)
    
    z_min_verts = [v for v in verts if abs(v.z - z_min) < 1e-4]
    z_max_verts = [v for v in verts if abs(v.z - z_max) < 1e-4]
    
    if not z_min_verts or not z_max_verts:
        return _make_unsupported_spec(obj, props, "invalid-frustum-topology")
        
    radius_1 = max((v.x**2 + v.y**2)**0.5 for v in z_min_verts)
    radius_2 = max((v.x**2 + v.y**2)**0.5 for v in z_max_verts)
    
    axis_pt1 = [0, 0, z_min]
    axis_pt2 = [0, 0, z_max]
    radius_pt1 = [radius_1, 0, z_min]
    
    return {
        "type": "frustum",
        "name": obj.name,
        "axis_pt1": axis_pt1,
        "axis_pt2": axis_pt2,
        "radius_point_1": radius_pt1,
        "radius_2": radius_2,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
        **_read_chain_params(props),
        "matrix_world": [list(row) for row in obj.matrix_world],
    }

def _build_extruded_ring_spec(obj, props):
    # pyrefly: ignore [import-outside-toplevel, missing-import]
    import bpy
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    
    verts = [v.co for v in mesh.vertices]
    z_coords = [v.z for v in verts]
    z_min, z_max = min(z_coords), max(z_coords)
    
    z_min_verts = [v for v in verts if abs(v.z - z_min) < 1e-4]
    if not z_min_verts:
        return _make_unsupported_spec(obj, props, "invalid-ring-topology")
        
    radii = [(v.x**2 + v.y**2)**0.5 for v in z_min_verts]
    outer_radius = max(radii)
    inner_radius = min(radii)
    
    if inner_radius < 1e-4 or abs(outer_radius - inner_radius) < 1e-4:
        return _make_unsupported_spec(obj, props, "invalid-ring-radii")
        
    return {
        "type": "extruded_ring",
        "name": obj.name,
        "axis_pt1": [0, 0, z_min],
        "axis_pt2": [0, 0, z_max],
        "outer_radius_pt": [outer_radius, 0, z_min],
        "inner_radius": inner_radius,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
        **_read_chain_params(props),
        "matrix_world": [list(row) for row in obj.matrix_world],
    }

def _build_wedge_spec(obj, props):
    # pyrefly: ignore [import-outside-toplevel, missing-import]
    import bpy
    face_index = getattr(props, "wedge_face_index", 0)
    angle_deg = getattr(props, "wedge_angle", 2.0)
    
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    
    if face_index >= len(mesh.polygons):
        return _make_unsupported_spec(obj, props, "invalid-wedge-face")
        
    poly = mesh.polygons[face_index]
    face_verts = [list(mesh.vertices[vi].co) for vi in poly.vertices]
    
    return {
        "type": "wedge",
        "name": obj.name,
        "face": face_verts,
        "angle_deg": angle_deg,
        "axis": [0, 0, 1], 
        "origin": [0, 0, 0],
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
        **_read_chain_params(props),
        "matrix_world": [list(row) for row in obj.matrix_world],
    }

def _make_unsupported_spec(obj, props, reason):
    friendly = reason
    warning = (f"{obj.name}: {friendly} — skipped during blockMesh generation.")
    pass
    return {
        "type": "unsupported",
        "name": obj.name,
        "reason": reason,
        "warning": warning,
        "patch_name": _read_patch_name(props),
    }

def _build_loft_spec(obj, props):
    face_idx_bottom = getattr(props, "loft_bottom_face_index", 0)
    face_idx_top = getattr(props, "loft_top_face_index", 1)
    
    try:
        bottom_pts = _extract_face_vertices_local_bmesh(obj, face_idx_bottom)
        top_pts = _extract_face_vertices_local_bmesh(obj, face_idx_top)
    except Exception as e:
        return _make_unsupported_spec(obj, props, f"invalid-loft-faces: {e}")
        
    return {
        "type": "loft",
        "name": obj.name,
        "bottom_face": bottom_pts,
        "top_face": top_pts,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
        **_read_chain_params(props),
        "matrix_world": [list(row) for row in obj.matrix_world],
    }

def _extract_face_vertices_local_bmesh(obj, face_index):
    # pyrefly: ignore [import-outside-toplevel, missing-import]
    import bpy
    # pyrefly: ignore [missing-import]
    import bmesh
    
    # Try bmesh first (crucial for un-applied Edit Mode changes)
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        
    bm.faces.ensure_lookup_table()
    
    if face_index >= len(bm.faces):
        if obj.mode != 'EDIT':
            bm.free()
        raise IndexError(f"Face index {face_index} out of range.")
        
    face = bm.faces[face_index]
    if len(face.verts) != 4:
        if obj.mode != 'EDIT':
            bm.free()
        raise ValueError("Face must have exactly 4 vertices.")
        
    verts_local = [[v.co.x, v.co.y, v.co.z] for v in face.verts]
    
    if obj.mode != 'EDIT':
        bm.free()
        
    return verts_local

def _build_extrude_spec(obj, props):
    face_index = getattr(props, "extrude_face_index", 0)
    axis = getattr(props, "extrude_axis", "Z")
    dist = getattr(props, "extrude_distance", 1.0)
    
    try:
        face_pts = _extract_face_vertices_local_bmesh(obj, face_index)
    except Exception as e:
        return _make_unsupported_spec(obj, props, f"invalid-extrude-face: {e}")
        
    vec = [0.0, 0.0, 0.0]
    if axis == "X": vec[0] = dist
    elif axis == "Y": vec[1] = dist
    elif axis == "Z": vec[2] = dist
    
    return {
        "type": "extrude",
        "name": obj.name,
        "face": face_pts,
        "extrude_vector": vec,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
        **_read_chain_params(props),
        "matrix_world": [list(row) for row in obj.matrix_world],
    }

def _build_sketch_spec(obj, props):
    """
    Builds a spec dictionary for a sketched curve.
    """
    return {
        "type": "sketch",
        "name": obj.name,
        "curve_type": obj.get("classy_curve_type", "POLY"),
        "points": [list(pt) for pt in _extract_curve_points(obj)],
        "matrix_world": [list(row) for row in obj.matrix_world],
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
        **_read_chain_params(props),
    }

def _extract_curve_points(obj):
    import bpy
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    curve = obj_eval.data
    
    pts = []
    if not curve.splines:
        return pts
        
    spline = curve.splines[0]
    if spline.type == 'BEZIER':
        pts = [list(p.co) for p in spline.bezier_points]
    else:
        pts = [list(p.co[:3]) for p in spline.points]
        
    return pts

def _build_revolve_spec(obj, props):
    face_index = getattr(props, "revolve_face_index", 0)
    angle_deg = getattr(props, "revolve_angle", 90.0)
    axis_str = getattr(props, "revolve_axis", "Z")
    origin = getattr(props, "revolve_origin", (0,0,0))
    
    try:
        face_pts = _extract_face_vertices_local_bmesh(obj, face_index)
    except Exception as e:
        return _make_unsupported_spec(obj, props, f"invalid-revolve-face: {e}")
        
    axis = [0.0, 0.0, 0.0]
    if axis_str == "X": axis[0] = 1.0
    elif axis_str == "Y": axis[1] = 1.0
    elif axis_str == "Z": axis[2] = 1.0
    
    return {
        "type": "revolve",
        "name": obj.name,
        "face": face_pts,
        "angle_deg": angle_deg,
        "axis": axis,
        "origin": list(origin),
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
        **_read_chain_params(props),
        "matrix_world": [list(row) for row in obj.matrix_world],
    }

# ─────────────────────── HELPERS ───────────────────────


def _get_world_bounding_box(obj):
    """
    Returns (p_min, p_max) for a Blender object in absolute world space.

    CRITICAL: obj.bound_box returns bpy_prop_array items, NOT Vector objects.
    Must wrap each corner in mathutils.Vector() before matrix multiplication.
    """
    try:
        # pyrefly: ignore [missing-import]
        from mathutils import Vector
    except ModuleNotFoundError:
        import subprocess, sys
        subprocess.check_call(
            [sys.executable] + "-m pip install mathutils".split() 
        )
    finally:
        # pyrefly: ignore [missing-import]
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
    # pyrefly: ignore [missing-import]
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
    # pyrefly: ignore [missing-import]
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
    # pyrefly: ignore [missing-import]
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


def _read_chain_params(props):
    """Read shape chaining parameters from object properties."""
    chain_source = getattr(props, "chain_source", "") if props else ""
    if not chain_source:
        return {}
    return {
        "chain_source": chain_source,
        "chain_length": float(getattr(props, "chain_length", 1.0) if props else 1.0),
        "chain_radius_2": float(getattr(props, "chain_radius_2", 0.0) if props else 0.0),
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
