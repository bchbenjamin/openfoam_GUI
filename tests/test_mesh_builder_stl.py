# tests/test_mesh_builder_stl.py
import pytest
import os
import importlib.util
import classy_blocks as cb

_mb_path = os.path.join(os.path.dirname(__file__), "..", "addon", "mesh_builder.py")
_spec = importlib.util.spec_from_file_location("mesh_builder", _mb_path)
_mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mb)

def test_build_block_plain():
    """A plain box block (no projection) builds correctly."""
    mesh = cb.Mesh()
    spec = {
        "type": "box",
        "name": "test_box",
        "p_min": [0, 0, 0],
        "p_max": [1, 1, 1],
        "cells": [10, 10, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "needs_self_projection": False,
    }
    _mb.build_block(mesh, spec)

def test_build_block_with_self_projection():
    """A block with self-projection adds project_side for all 6 faces."""
    mesh = cb.Mesh()
    spec = {
        "type": "box",
        "name": "cylinder",
        "p_min": [0, 0, 0],
        "p_max": [1, 1, 2],
        "cells": [10, 10, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "needs_self_projection": True,
        "self_stl_name": "cylinder.stl",
    }
    _mb.build_block(mesh, spec)

def test_build_block_with_user_stl():
    """A block with user-specified STL projection (terrain)."""
    mesh = cb.Mesh()
    spec = {
        "type": "box",
        "name": "terrain_box",
        "p_min": [0, 0, 0],
        "p_max": [1, 1, 1],
        "cells": [10, 10, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "needs_self_projection": False,
        "stl_projections": {"top": "terrain.stl"},
    }
    _mb.build_block(mesh, spec)

def test_build_from_spec_end_to_end(tmp_path):
    """Full spec → blockMeshDict file."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [
            {
                "type": "box",
                "name": "stl_box",
                "p_min": [0, 0, 0],
                "p_max": [1, 1, 1],
                "cells": [10, 10, 10],
                "grading_type": "RATIO",
                "grading": [1.0, 1.0, 1.0],
                "needs_self_projection": True,
                "self_stl_name": "terrain.stl",
                "stl_projections": {"top": "terrain.stl"},
            }
        ],
        "merge_tolerance": 1e-4
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()

    content = output_path.read_text()
    assert "project" in content
    assert "terrain.stl" in content
