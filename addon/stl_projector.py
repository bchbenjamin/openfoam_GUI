"""
STL Projector module.

Provides STL file loading and validation using PyVista. This module serves a single purpose:

1. VALIDATION: Before running the expensive blockMesh pipeline, this
   module can validate that an STL file is well-formed (manifold, reasonable
   triangle count).

NATIVE PROJECTION NOTE:
   The primary projection path in this add-on uses classy_blocks' native
   project_side() + add_geometry() mechanism, which emits 'project' directives
   into the blockMeshDict. OpenFOAM's blockMesh then resolves these at runtime
   using its own searchableSurface infrastructure. This is accurate because
   it projects ALL mesh points on the face (not just the 4/8 control vertices)
   and respects mesh grading and curvature interpolation.

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
