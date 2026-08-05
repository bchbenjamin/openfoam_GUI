# tests/test_chain_builder.py
# Tests for shape chaining (pipe networks) via mesh_builder.
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


def test_chain_cylinder_from_cylinder(tmp_path) -> None:
    """Chain a cylinder from another cylinder (same radius pipe extension).

    Args:
      tmp_path: 

    Returns:

    """
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [
            {
                "type": "cylinder",
                "name": "source_pipe",
                "axis_pt1": [0, 0, 0],
                "axis_pt2": [0, 0, 2],
                "radius_point": [1, 0, 0],
                "radius": 1.0,
                "cells": [5, 8, 10],
                "grading_type": "RATIO",
                "grading": [1.0, 1.0, 1.0],
            },
            {
                "type": "cylinder",
                "name": "chained_pipe",
                "axis_pt1": [0, 0, 2],
                "axis_pt2": [0, 0, 4],
                "radius_point": [1, 0, 2],
                "radius": 1.0,
                "cells": [5, 8, 10],
                "grading_type": "RATIO",
                "grading": [1.0, 1.0, 1.0],
                "chain_source": "source_pipe",
                "chain_length": 2.0,
            },
        ],
        "merge_tolerance": 1e-4,
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    # Two O-grid sections: 12 + 12 = 24 hex blocks
    assert content.count("hex") >= 24


def test_chain_frustum_from_cylinder(tmp_path) -> None:
    """Chain a frustum (taper) from a cylinder.

    Args:
      tmp_path: 

    Returns:

    """
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [
            {
                "type": "cylinder",
                "name": "inlet_pipe",
                "axis_pt1": [0, 0, 0],
                "axis_pt2": [0, 0, 2],
                "radius_point": [1, 0, 0],
                "radius": 1.0,
                "cells": [5, 8, 10],
                "grading_type": "RATIO",
                "grading": [1.0, 1.0, 1.0],
            },
            {
                "type": "frustum",
                "name": "taper_section",
                "axis_pt1": [0, 0, 2],
                "axis_pt2": [0, 0, 4],
                "radius_point_1": [1, 0, 2],
                "radius_1": 1.0,
                "radius_2": 0.5,
                "cells": [5, 8, 10],
                "grading_type": "RATIO",
                "grading": [1.0, 1.0, 1.0],
                "chain_source": "inlet_pipe",
                "chain_length": 2.0,
                "chain_radius_2": 0.5,
            },
        ],
        "merge_tolerance": 1e-4,
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert content.count("hex") >= 24


def test_chain_missing_source_skipped(tmp_path) -> None:
    """Chaining from a non-existent source is gracefully skipped.

    Args:
      tmp_path: 

    Returns:

    """
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [
            {
                "type": "box",
                "name": "a_box",
                "p_min": [0, 0, 0],
                "p_max": [1, 1, 1],
                "cells": [10, 10, 10],
                "grading_type": "RATIO",
                "grading": [1.0, 1.0, 1.0],
            },
            {
                "type": "cylinder",
                "name": "orphan_pipe",
                "axis_pt1": [5, 0, 0],
                "axis_pt2": [5, 0, 2],
                "radius_point": [6, 0, 0],
                "radius": 1.0,
                "cells": [5, 8, 10],
                "grading_type": "RATIO",
                "grading": [1.0, 1.0, 1.0],
                "chain_source": "nonexistent_source",
                "chain_length": 2.0,
            },
        ],
        "merge_tolerance": 1e-4,
    }

    # Should not crash — the orphan pipe is skipped, but the box is built
    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
