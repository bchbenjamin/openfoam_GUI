"""
STL Projector module.

Provides STL file loading, validation, and point-to-surface projection using
PyVista. This module serves two purposes:

1. VALIDATION & PREVIEW: Before running the expensive blockMesh pipeline, this
   module can validate that an STL file is well-formed (manifold, reasonable
   triangle count) and preview where block vertices would land on the surface.

2. PYTHON-SIDE FALLBACK: If needed, project_face_to_stl() can pre-warp block
   control vertices onto an STL surface. However, this is inferior to the native
   OpenFOAM projection mechanism (see NATIVE VS FALLBACK NOTE below).

NATIVE VS FALLBACK NOTE:
   The primary projection path in this add-on uses classy_blocks' native
   project_side() + add_geometry() mechanism, which emits 'project' directives
   into the blockMeshDict. OpenFOAM's blockMesh then resolves these at runtime
   using its own searchableSurface infrastructure. This is MORE ACCURATE because
   it projects ALL mesh points on the face (not just the 4/8 control vertices)
   and respects mesh grading and curvature interpolation.

   The Python-side pre-warping in this module only moves the control vertices;
   blockMesh will then linearly interpolate between those warped corners,
   producing a poor approximation of curved terrain with many cells. Use the
   native mechanism whenever possible.

No top-level 'import bpy' — this module is standalone-testable.

CALLED BY: operators.py → CLASSY_OT_project_to_stl
"""

import os
import numpy as np

# Lazy-import pyvista to keep module importable even without it installed
_pv = None

def _get_pyvista():
    global _pv
    if _pv is None:
        import pyvista
        _pv = pyvista
    return _pv


# ─────────────────────── STL LOADING ───────────────────────

_HIGH_TRIANGLE_THRESHOLD = 500_000


def load_stl(filepath: str):
    """
    Load and validate an STL file.

    Args:
        filepath: Absolute path to an STL file.

    Returns:
        pyvista.PolyData mesh object.

    Raises:
        FileNotFoundError: if the file doesn't exist.
        ValueError: if the file is empty or cannot be parsed.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"STL file not found: {filepath}")

    pv = _get_pyvista()
    try:
        surface = pv.read(filepath)
    except Exception as e:
        raise ValueError(
            f"Failed to read STL file '{os.path.basename(filepath)}': {e}\n"
            "Ensure it is a valid binary or ASCII STL."
        ) from e

    if surface.n_points == 0 or surface.n_cells == 0:
        raise ValueError(
            f"STL file '{os.path.basename(filepath)}' is empty "
            f"(0 points or 0 triangles)."
        )

    return surface


def validate_stl(filepath: str) -> dict:
    """
    Validate an STL file and return a status dict.

    Returns:
        dict with keys:
            valid (bool): True if the file loaded without error.
            n_triangles (int): Number of triangles.
            is_manifold (bool): True if the surface is watertight.
            warnings (list[str]): Any non-fatal warnings.
            error (str|None): Error message if invalid.
    """
    result = {
        "valid": False,
        "n_triangles": 0,
        "is_manifold": False,
        "warnings": [],
        "error": None,
    }

    try:
        surface = load_stl(filepath)
    except (FileNotFoundError, ValueError) as e:
        result["error"] = str(e)
        return result

    result["valid"] = True
    result["n_triangles"] = surface.n_cells

    # Manifold check
    try:
        result["is_manifold"] = bool(surface.is_manifold)
    except Exception:
        result["is_manifold"] = False
        result["warnings"].append(
            "Could not determine manifold status — PyVista version may lack "
            "is_manifold support."
        )

    if not result["is_manifold"]:
        result["warnings"].append(
            f"STL '{os.path.basename(filepath)}' is not manifold (watertight). "
            "Projection may produce unexpected results at surface boundaries."
        )

    if result["n_triangles"] > _HIGH_TRIANGLE_THRESHOLD:
        result["warnings"].append(
            f"STL has {result['n_triangles']:,} triangles (>{_HIGH_TRIANGLE_THRESHOLD:,}). "
            "This may slow down blockMesh projection. Consider decimating."
        )

    return result


# ─────────────────────── POINT PROJECTION ───────────────────────

_DIRECTION_VECTORS = {
    "x": np.array([1.0, 0.0, 0.0]),
    "-x": np.array([-1.0, 0.0, 0.0]),
    "y": np.array([0.0, 1.0, 0.0]),
    "-y": np.array([0.0, -1.0, 0.0]),
    "z": np.array([0.0, 0.0, 1.0]),
    "-z": np.array([0.0, 0.0, -1.0]),
}


def project_points_to_surface(
    points,
    surface,
    direction: str = "z",
    max_distance: float = None,
):
    """
    Project points onto a triangulated surface along a given direction.

    For each input point, a ray is cast along both +direction and -direction.
    The closest intersection is used. If no intersection is found, the point
    falls back to nearest-point-on-surface projection.

    Args:
        points: (N, 3) array-like of input coordinates.
        surface: pyvista.PolyData triangulated surface.
        direction: 'x', 'y', 'z', '-x', '-y', '-z'. Default 'z'.
        max_distance: If set, fallback points further than this are left
                      unchanged and flagged in warnings.

    Returns:
        tuple (projected_points, warnings):
            projected_points: np.ndarray (N, 3) of projected coordinates.
            warnings: list of warning strings for missed rays / fallback.
    """
    pts = np.asarray(points, dtype=float)
    if pts.ndim == 1:
        pts = pts.reshape(1, 3)

    n_points = len(pts)
    projected = pts.copy()
    warnings = []

    dir_key = direction.lower().strip()
    if dir_key not in _DIRECTION_VECTORS:
        raise ValueError(
            f"Unknown direction '{direction}'. "
            f"Valid: {', '.join(_DIRECTION_VECTORS.keys())}"
        )
    dir_vec = _DIRECTION_VECTORS[dir_key]

    # Determine the axis index for the projection direction
    axis_idx = int(np.argmax(np.abs(dir_vec)))

    for i in range(n_points):
        origin = pts[i]
        hit = False

        # Try ray in both directions along the axis
        for sign in [1.0, -1.0]:
            ray_dir = dir_vec * sign
            # Cast ray from far away along the axis toward the surface
            ray_start = origin.copy()
            ray_end = origin + ray_dir * 1e6

            try:
                intersection_pts, _ = surface.ray_trace(ray_start, ray_end)
                if len(intersection_pts) > 0:
                    # Pick the closest intersection to the original point
                    dists = np.linalg.norm(intersection_pts - origin, axis=1)
                    closest_idx = int(np.argmin(dists))
                    projected[i] = intersection_pts[closest_idx]
                    hit = True
                    break
            except Exception:
                continue

        if not hit:
            # Fallback: nearest point on surface
            try:
                closest_idx = surface.find_closest_point(origin)
                nearest_pt = np.array(surface.points[closest_idx])
                dist = float(np.linalg.norm(nearest_pt - origin))

                if max_distance is not None and dist > max_distance:
                    warnings.append(
                        f"Point {i} at {origin.tolist()}: ray missed surface "
                        f"and nearest point is {dist:.3f} away "
                        f"(> max_distance={max_distance}). Left unchanged."
                    )
                else:
                    projected[i] = nearest_pt
                    warnings.append(
                        f"Point {i} at {origin.tolist()}: ray missed surface, "
                        f"fell back to nearest-point ({dist:.3f} away)."
                    )
            except Exception as e:
                warnings.append(
                    f"Point {i} at {origin.tolist()}: ray missed surface "
                    f"and nearest-point lookup failed: {e}. Left unchanged."
                )

    return projected, warnings


# ─────────────────────── FACE PROJECTION ───────────────────────

# Map of block-type face names to the vertex indices they control.
# For box: 8 vertices. The named faces correspond to groups of 4 corner indices.
_BOX_FACE_VERTEX_INDICES = {
    "bottom": [0, 1, 2, 3],    # z-min face
    "top":    [4, 5, 6, 7],    # z-max face
    "front":  [0, 1, 5, 4],    # y-min face
    "back":   [2, 3, 7, 6],    # y-max face
    "left":   [0, 3, 7, 4],    # x-min face
    "right":  [1, 2, 6, 5],    # x-max face
}


def project_face_to_stl(spec: dict, face_name: str, stl_path: str,
                         direction: str = "z") -> dict:
    """
    Project a named face's control points onto an STL surface.

    Takes a block spec dict (as produced by geometry_extractor.py), loads the
    STL, projects the named face's vertices, and returns an updated spec dict
    with the projected point positions and a 'projected' marker.

    This is the PYTHON-SIDE FALLBACK approach. The primary projection path
    uses classy_blocks' native project_side() mechanism (see mesh_builder.py).

    Args:
        spec: Block specification dict (must have 'type' key).
        face_name: Face to project (e.g., 'top', 'bottom').
        stl_path: Path to the STL file.
        direction: Projection direction ('x', 'y', 'z', '-x', '-y', '-z').

    Returns:
        Updated spec dict with projected coordinates and metadata.
    """
    surface = load_stl(stl_path)
    updated = dict(spec)

    block_type = spec.get("type", "box")

    if block_type == "box":
        # Extract the 8 box corners from p_min / p_max
        p_min = np.array(spec["p_min"], dtype=float)
        p_max = np.array(spec["p_max"], dtype=float)

        corners = np.array([
            [p_min[0], p_min[1], p_min[2]],  # 0
            [p_max[0], p_min[1], p_min[2]],  # 1
            [p_max[0], p_max[1], p_min[2]],  # 2
            [p_min[0], p_max[1], p_min[2]],  # 3
            [p_min[0], p_min[1], p_max[2]],  # 4
            [p_max[0], p_min[1], p_max[2]],  # 5
            [p_max[0], p_max[1], p_max[2]],  # 6
            [p_min[0], p_max[1], p_max[2]],  # 7
        ])

        if face_name not in _BOX_FACE_VERTEX_INDICES:
            raise ValueError(
                f"Unknown face name '{face_name}' for box. "
                f"Valid: {', '.join(_BOX_FACE_VERTEX_INDICES.keys())}"
            )

        indices = _BOX_FACE_VERTEX_INDICES[face_name]
        face_pts = corners[indices]
        projected_pts, proj_warnings = project_points_to_surface(
            face_pts, surface, direction=direction
        )

        # Write back the projected positions
        corners[indices] = projected_pts
        updated["p_min"] = corners.min(axis=0).tolist()
        updated["p_max"] = corners.max(axis=0).tolist()

    elif block_type in ("extrude", "loft"):
        # For extrude/loft, project the 'face' or 'bottom_face'/'top_face'
        face_key = None
        if block_type == "extrude" and face_name in ("bottom", "face"):
            face_key = "face"
        elif block_type == "loft":
            if face_name in ("bottom", "bottom_face"):
                face_key = "bottom_face"
            elif face_name in ("top", "top_face"):
                face_key = "top_face"

        if face_key and face_key in spec:
            face_pts = np.array(spec[face_key], dtype=float)
            projected_pts, proj_warnings = project_points_to_surface(
                face_pts, surface, direction=direction
            )
            updated[face_key] = projected_pts.tolist()
        else:
            proj_warnings = [
                f"Cannot project face '{face_name}' for block type "
                f"'{block_type}': face key not found in spec."
            ]
    else:
        proj_warnings = [
            f"Python-side projection not supported for block type "
            f"'{block_type}'. Use the native OpenFOAM projection via "
            f"project_side() instead."
        ]

    # Tag the spec so mesh_builder knows this face was projected
    updated.setdefault("projected", {})
    updated["projected"][face_name] = {
        "stl_path": stl_path,
        "direction": direction,
        "method": "python_fallback",
        "warnings": proj_warnings if 'proj_warnings' in dir() else [],
    }

    return updated
