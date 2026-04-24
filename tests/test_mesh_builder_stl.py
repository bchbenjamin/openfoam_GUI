# tests/test_mesh_builder_stl.py
# Tests for mesh_builder.py — box, extrude, revolve, STL projection.
import pytest
import os
import importlib.util
import classy_blocks as cb

_mb_path = os.path.join(os.path.dirname(__file__), "..", "addon", "mesh_builder.py")
_spec = importlib.util.spec_from_file_location("mesh_builder", _mb_path)
_mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mb)


def test_build_box_plain():
    """A plain box block builds correctly."""
    mesh = cb.Mesh()
    spec = {
        "type": "box",
        "name": "test_box",
        "p_min": [0, 0, 0],
        "p_max": [1, 1, 1],
        "cells": [10, 10, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    _mb.build_block(mesh, spec)


def test_build_box_with_stl_projection():
    """A box with STL projection registers geometry and projects."""
    mesh = cb.Mesh()
    spec = {
        "type": "box",
        "name": "terrain_box",
        "p_min": [0, 0, 0],
        "p_max": [1, 1, 1],
        "cells": [10, 10, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "stl_projections": {"top": "terrain.stl"},
    }
    _mb.build_block(mesh, spec)


def test_build_extrude():
    """An extrude block builds correctly."""
    mesh = cb.Mesh()
    spec = {
        "type": "extrude",
        "name": "test_extrude",
        "face": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
        "extrude_vector": [0, 0, 1],
        "cells": [5, 5, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    _mb.build_block(mesh, spec)


def test_build_revolve():
    """A revolve block builds correctly."""
    mesh = cb.Mesh()
    spec = {
        "type": "revolve",
        "name": "test_revolve",
        "face": [[0.5, 0, 0], [1, 0, 0], [1, 1, 0], [0.5, 1, 0]],
        "angle_deg": 90.0,
        "axis": [0, 1, 0],
        "origin": [0, 0, 0],
        "cells": [5, 5, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    _mb.build_block(mesh, spec)


def test_unknown_block_type_raises():
    """Unknown block type raises ValueError."""
    mesh = cb.Mesh()
    spec = {
        "type": "invalid_type",
        "name": "bad_block",
    }
    with pytest.raises(ValueError, match="Unknown block type"):
        _mb.build_block(mesh, spec)


def test_build_from_spec_box_end_to_end(tmp_path):
    """Full spec → blockMeshDict for a box."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [{
            "type": "box",
            "name": "test_box",
            "p_min": [0, 0, 0],
            "p_max": [1, 1, 1],
            "cells": [10, 10, 10],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }],
        "merge_tolerance": 1e-4
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert "hex" in content


def test_build_from_spec_with_stl_projection(tmp_path):
    """Full spec with STL projection → blockMeshDict contains geometry section."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [{
            "type": "box",
            "name": "terrain_box",
            "p_min": [0, 0, 0],
            "p_max": [1, 1, 1],
            "cells": [10, 10, 10],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
            "stl_projections": {"top": "terrain.stl"},
        }],
        "merge_tolerance": 1e-4
    }

    _mb.build_from_spec(spec, str(output_path))
    content = output_path.read_text()
    assert "geometry" in content
    assert "terrain.stl" in content
    assert "project" in content


def test_build_from_spec_extrude_end_to_end(tmp_path):
    """Full spec → blockMeshDict for an extrude."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [{
            "type": "extrude",
            "name": "test_extrude",
            "face": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
            "extrude_vector": [0, 0, 2],
            "cells": [5, 5, 10],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }],
        "merge_tolerance": 1e-4
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()


def test_build_from_spec_revolve_end_to_end(tmp_path):
    """Full spec → blockMeshDict for a revolve."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [{
            "type": "revolve",
            "name": "test_revolve",
            "face": [[0.5, 0, 0], [1, 0, 0], [1, 1, 0], [0.5, 1, 0]],
            "angle_deg": 90.0,
            "axis": [0, 1, 0],
            "origin": [0, 0, 0],
            "cells": [5, 5, 10],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }],
        "merge_tolerance": 1e-4
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
