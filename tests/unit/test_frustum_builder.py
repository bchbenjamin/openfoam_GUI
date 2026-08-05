# tests/test_frustum_builder.py
# Tests for frustum (truncated cone) building via mesh_builder.
import pytest
import os
import sys
import importlib.util

os.environ.setdefault("NUMBA_DISABLE_JIT", "1")

sys.path.insert(0, os.path.dirname(__file__))
from _cb_compat import cb

_mb_path = os.path.join(os.path.dirname(__file__), "../..", "addon", "mesh_builder.py")
_spec = importlib.util.spec_from_file_location("mesh_builder", _mb_path)
_mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mb)


def test_build_frustum_basic() -> None:
    """A frustum block builds correctly with different start/end radii."""
    mesh = cb.Mesh()
    spec = {
        "type": "frustum",
        "name": "test_frustum",
        "axis_pt1": [0, 0, 0],
        "axis_pt2": [0, 0, 2],
        "radius_point_1": [1, 0, 0],
        "radius_1": 1.0,
        "radius_2": 0.5,
        "cells": [5, 8, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    result = _mb.build_block(mesh, spec)
    assert result is True


def test_build_frustum_pointy_cone() -> None:
    """A frustum with radius_2=very small (near-pointy cone)."""
    mesh = cb.Mesh()
    spec = {
        "type": "frustum",
        "name": "pointy_cone",
        "axis_pt1": [0, 0, 0],
        "axis_pt2": [0, 0, 3],
        "radius_point_1": [1, 0, 0],
        "radius_1": 1.0,
        "radius_2": 0.01,  # Near-zero (can't be exactly 0 for O-grid)
        "cells": [5, 8, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    result = _mb.build_block(mesh, spec)
    assert result is True


def test_build_frustum_equal_radii() -> None:
    """A frustum with equal radii is effectively a cylinder."""
    mesh = cb.Mesh()
    spec = {
        "type": "frustum",
        "name": "cylinder_as_frustum",
        "axis_pt1": [0, 0, 0],
        "axis_pt2": [0, 0, 2],
        "radius_point_1": [1, 0, 0],
        "radius_1": 1.0,
        "radius_2": 1.0,
        "cells": [5, 8, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    result = _mb.build_block(mesh, spec)
    assert result is True


def test_build_frustum_end_to_end(tmp_path) -> None:
    """Full spec → blockMeshDict for a frustum.

    Args:
      tmp_path: 

    Returns:

    """
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [{
            "type": "frustum",
            "name": "test_frustum",
            "axis_pt1": [0, 0, 0],
            "axis_pt2": [0, 0, 2],
            "radius_point_1": [1, 0, 0],
            "radius_1": 1.0,
            "radius_2": 0.5,
            "cells": [5, 8, 10],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }],
        "merge_tolerance": 1e-4
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert "hex" in content
    # Frustum generates O-grid blocks like cylinder
    assert content.count("hex") >= 12


def test_build_frustum_with_grading() -> None:
    """Frustum with START_SIZE grading mode."""
    mesh = cb.Mesh()
    spec = {
        "type": "frustum",
        "name": "graded_frustum",
        "axis_pt1": [0, 0, 0],
        "axis_pt2": [0, 0, 2],
        "radius_point_1": [1, 0, 0],
        "radius_1": 1.0,
        "radius_2": 0.3,
        "cells": [5, 8, 10],
        "grading_type": "START_SIZE",
        "grading": [1.0, 1.0, 1.0],
        "start_size": 0.01,
        "end_size": 0.01,
    }
    result = _mb.build_block(mesh, spec)
    assert result is True
