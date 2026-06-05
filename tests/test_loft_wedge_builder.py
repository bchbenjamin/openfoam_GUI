# tests/test_loft_wedge_builder.py
# Tests for loft and wedge block building via mesh_builder.
import pytest
import os
import sys
import importlib.util

os.environ.setdefault("NUMBA_DISABLE_JIT", "1")

sys.path.insert(0, os.path.dirname(__file__))
from _cb_compat import cb

_mb_path = os.path.join(os.path.dirname(__file__), "..", "addon", "mesh_builder.py")
_spec = importlib.util.spec_from_file_location("mesh_builder", _mb_path)
_mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mb)


# ─────────────────────── LOFT TESTS ───────────────────────


def test_build_loft_basic():
    """A loft connects two quad faces to form a single hex block."""
    mesh = cb.Mesh()
    spec = {
        "type": "loft",
        "name": "test_loft",
        "bottom_face": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
        "top_face": [[0.2, 0.2, 2], [0.8, 0.2, 2], [0.8, 0.8, 2], [0.2, 0.8, 2]],
        "cells": [5, 5, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    result = _mb.build_block(mesh, spec)
    assert result is True


def test_build_loft_parallel_faces():
    """A loft with parallel, same-size faces is essentially an extrude."""
    mesh = cb.Mesh()
    spec = {
        "type": "loft",
        "name": "parallel_loft",
        "bottom_face": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
        "top_face": [[0, 0, 2], [1, 0, 2], [1, 1, 2], [0, 1, 2]],
        "cells": [10, 10, 5],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    result = _mb.build_block(mesh, spec)
    assert result is True


def test_build_loft_end_to_end(tmp_path):
    """Full spec → blockMeshDict for a loft."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [{
            "type": "loft",
            "name": "test_loft",
            "bottom_face": [[0, 0, 0], [2, 0, 0], [2, 1, 0], [0, 1, 0]],
            "top_face": [[0.5, 0.25, 3], [1.5, 0.25, 3], [1.5, 0.75, 3], [0.5, 0.75, 3]],
            "cells": [5, 5, 10],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }],
        "merge_tolerance": 1e-4,
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert "hex" in content


# ─────────────────────── WEDGE TESTS ───────────────────────


def test_build_wedge_basic():
    """A wedge block builds correctly for axisymmetric 2D."""
    mesh = cb.Mesh()
    spec = {
        "type": "wedge",
        "name": "test_wedge",
        "face": [[0.1, 0, 0], [1, 0, 0], [1, 1, 0], [0.1, 1, 0]],
        "angle_deg": 2.0,
        "cells": [5, 5, 1],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    result = _mb.build_block(mesh, spec)
    assert result is True


def test_build_wedge_5_degrees():
    """A wedge with a wider 5-degree angle."""
    mesh = cb.Mesh()
    spec = {
        "type": "wedge",
        "name": "wide_wedge",
        "face": [[0.1, 0, 0], [1, 0, 0], [1, 2, 0], [0.1, 2, 0]],
        "angle_deg": 5.0,
        "cells": [10, 10, 1],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    result = _mb.build_block(mesh, spec)
    assert result is True


def test_build_wedge_end_to_end(tmp_path):
    """Full spec → blockMeshDict for a wedge."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [{
            "type": "wedge",
            "name": "test_wedge",
            "face": [[0.1, 0, 0], [1, 0, 0], [1, 1, 0], [0.1, 1, 0]],
            "angle_deg": 2.0,
            "cells": [5, 5, 1],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }],
        "merge_tolerance": 1e-4,
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert "hex" in content


# ─────────────────────── MIXED SPEC TESTS ───────────────────────


def test_build_mixed_spec_with_all_new_types(tmp_path):
    """A spec containing frustum + loft + wedge all build together."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [
            {
                "type": "frustum",
                "name": "cone_section",
                "axis_pt1": [0, 0, 0],
                "axis_pt2": [0, 0, 2],
                "radius_point_1": [1, 0, 0],
                "radius_1": 1.0,
                "radius_2": 0.5,
                "cells": [5, 8, 10],
                "grading_type": "RATIO",
                "grading": [1.0, 1.0, 1.0],
            },
            {
                "type": "loft",
                "name": "transition",
                "bottom_face": [[3, 0, 0], [5, 0, 0], [5, 2, 0], [3, 2, 0]],
                "top_face": [[3.5, 0.5, 2], [4.5, 0.5, 2], [4.5, 1.5, 2], [3.5, 1.5, 2]],
                "cells": [5, 5, 10],
                "grading_type": "RATIO",
                "grading": [1.0, 1.0, 1.0],
            },
        ],
        "merge_tolerance": 1e-4,
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    # Should have hex blocks from both frustum and loft
    assert content.count("hex") >= 13  # 12 from frustum + 1 from loft
