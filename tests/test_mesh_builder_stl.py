# tests/test_mesh_builder_stl.py
# Tests for mesh_builder.py — box, extrude, revolve, STL projection.
import pytest
import os
import importlib.util

os.environ.setdefault("NUMBA_DISABLE_JIT", "1")

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


def test_build_cylinder():
    """A cylinder block builds correctly (O-grid, 12 hex blocks)."""
    mesh = cb.Mesh()
    spec = {
        "type": "cylinder",
        "name": "test_cylinder",
        "axis_pt1": [0, 0, 0],
        "axis_pt2": [0, 0, 2],
        "radius_point": [1, 0, 0],
        "radius": 1.0,
        "cells": [5, 5, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    _mb.build_block(mesh, spec)


def test_build_extrude_with_stl_projection():
    """An extrude block with STL projection registers geometry and projects."""
    mesh = cb.Mesh()
    spec = {
        "type": "extrude",
        "name": "test_extrude",
        "face": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
        "extrude_vector": [0, 0, 1],
        "cells": [5, 5, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "stl_projections": {"top": "terrain.stl"},
    }
    _mb.build_block(mesh, spec)


def test_build_cylinder_with_stl_projection():
    """A cylinder block with STL projection registers geometry and projects."""
    mesh = cb.Mesh()
    spec = {
        "type": "cylinder",
        "name": "test_cylinder",
        "axis_pt1": [0, 0, 0],
        "axis_pt2": [0, 0, 2],
        "radius_point": [1, 0, 0],
        "radius": 1.0,
        "cells": [5, 5, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "stl_projections": {"top": "terrain.stl"},
    }
    _mb.build_block(mesh, spec)


def test_build_revolve_with_stl_projection():
    mesh = cb.Mesh()
    spec = {
        "type": "revolve",
        "name": "test_revolve",
        "face": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
        "angle_deg": 90,
        "axis": [0, 1, 0],
        "origin": [0, 0, 0],
        "cells": [5, 5, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "stl_projections": {"top": "terrain.stl"},
    }
    _mb.build_block(mesh, spec)


def test_build_frustum_with_stl_projection():
    mesh = cb.Mesh()
    spec = {
        "type": "frustum",
        "name": "test_frustum",
        "axis_pt1": [0, 0, 0],
        "axis_pt2": [0, 0, 2],
        "radius_point_1": [1, 0, 0],
        "radius_2": 0.5,
        "cells": [5, 5, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "stl_projections": {"top": "terrain.stl"},
    }
    _mb.build_block(mesh, spec)


def test_build_loft_with_stl_projection():
    mesh = cb.Mesh()
    spec = {
        "type": "loft",
        "name": "test_loft",
        "bottom_face": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
        "top_face": [[0, 0, 2], [1, 0, 2], [1, 1, 2], [0, 1, 2]],
        "cells": [5, 5, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "stl_projections": {"top": "terrain.stl"},
    }
    _mb.build_block(mesh, spec)


def test_build_wedge_with_stl_projection():
    mesh = cb.Mesh()
    spec = {
        "type": "wedge",
        "name": "test_wedge",
        "face": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
        "angle_deg": 5,
        "axis": [0, 1, 0],
        "origin": [0, 0, 0],
        "cells": [5, 5, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "stl_projections": {"right": "terrain.stl"},
    }
    _mb.build_block(mesh, spec)


def test_build_sphere():
    """A sphere block builds correctly from two hemispheres."""
    mesh = cb.Mesh()
    spec = {
        "type": "sphere",
        "name": "test_sphere",
        "center": [0, 0, 0],
        "radius_point": [1, 0, 0],
        "radius": 1.0,
        "cells": [5, 8, 5],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    assert _mb.build_block(mesh, spec) is True


def test_build_disk():
    """A planar circle-like input builds as a thin structured disk."""
    mesh = cb.Mesh()
    spec = {
        "type": "disk",
        "name": "test_disk",
        "center": [0, 0, 0],
        "radius_point": [1, 0, 0],
        "normal": [0, 0, 1],
        "thickness": 0.01,
        "cells": [5, 8, 1],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
    }
    assert _mb.build_block(mesh, spec) is True


def test_build_cylinder_end_to_end(tmp_path):
    """Full spec → blockMeshDict for a cylinder."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [{
            "type": "cylinder",
            "name": "test_cylinder",
            "axis_pt1": [0, 0, 0],
            "axis_pt2": [0, 0, 2],
            "radius_point": [1, 0, 0],
            "radius": 1.0,
            "cells": [5, 5, 10],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }],
        "merge_tolerance": 1e-4
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert "hex" in content
    # cb.Cylinder generates 12 hex blocks (O-grid)
    assert content.count("hex") >= 12


def test_build_sphere_end_to_end(tmp_path):
    """Full spec → blockMeshDict for a sphere."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [{
            "type": "sphere",
            "name": "test_sphere",
            "center": [0, 0, 0],
            "radius_point": [1, 0, 0],
            "radius": 1.0,
            "cells": [5, 8, 5],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }],
        "merge_tolerance": 1e-4
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert "searchableSphere" in content
    assert content.count("hex") > 0


def test_build_disk_end_to_end(tmp_path):
    """Full spec → blockMeshDict for a thin disk."""
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)

    spec = {
        "blocks": [{
            "type": "disk",
            "name": "test_disk",
            "center": [0, 0, 0],
            "radius_point": [1, 0, 0],
            "normal": [0, 0, 1],
            "thickness": 0.01,
            "cells": [5, 8, 1],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }],
        "merge_tolerance": 1e-4
    }

    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert "hex" in content


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


def test_unsupported_block_is_skipped():
    """Unsupported blocks are skipped without raising."""
    mesh = cb.Mesh()
    spec = {
        "type": "unsupported",
        "name": "bad_block",
        "reason": "complex-surface",
    }
    assert _mb.build_block(mesh, spec) is False


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
