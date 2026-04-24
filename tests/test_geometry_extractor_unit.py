# tests/test_geometry_extractor_unit.py
# Unit tests for geometry_extractor.py — auto-detection dispatch.
#
# HOW TO RUN:
#   cd ~/classy_blender_mesh
#   python3 -m pytest tests/test_geometry_extractor_unit.py -v
#
# NOTE: The auto-detection pipeline uses bmesh (Blender-only) and PyVista
# for shape classification. In these unit tests we mock those dependencies
# and test the fallback behavior + dispatch routing.

import sys
import os
import types
from unittest.mock import MagicMock, patch
import importlib.util
import math


# ──────────────────────────────────────────────────────────────────────
# Mock bpy and dependencies BEFORE importing geometry_extractor
# ──────────────────────────────────────────────────────────────────────

class _MockVector:
    """Minimal Vector replacement that supports @ (matmul) and indexing."""
    def __init__(self, data):
        self._data = list(data)
        self.x = self._data[0] if len(self._data) > 0 else 0.0
        self.y = self._data[1] if len(self._data) > 1 else 0.0
        self.z = self._data[2] if len(self._data) > 2 else 0.0

    def __getitem__(self, idx):
        return self._data[idx]

    def __len__(self):
        return len(self._data)


class _MockMatrix:
    def __init__(self, translation=(0, 0, 0)):
        self._tx, self._ty, self._tz = translation

    def __matmul__(self, other):
        if isinstance(other, (list, tuple)):
            other = _MockVector(other)
        return _MockVector([
            other[0] + self._tx,
            other[1] + self._ty,
            other[2] + self._tz,
        ])


def _make_mock_object(name, bound_box, matrix_world, props_dict=None):
    """Creates a mock Blender mesh object."""
    obj = MagicMock()
    obj.name = name
    obj.type = 'MESH'
    obj.bound_box = bound_box
    obj.matrix_world = matrix_world

    if props_dict is not None:
        class _Props:
            pass
        mock_props = _Props()
        for key, value in props_dict.items():
            setattr(mock_props, key, value)
        obj.classy_block_props = mock_props
    else:
        obj.classy_block_props = None

    return obj


# Standard unit cube bounding box
_UNIT_CUBE_BBOX = [
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
    (-1, -1,  1), (1, -1,  1), (1, 1,  1), (-1, 1,  1),
]


# ──────────────────────────────────────────────────────────────────────
# Load geometry_extractor with mocked bpy/bmesh
# ──────────────────────────────────────────────────────────────────────

def _load_geometry_extractor():
    mock_bpy = types.ModuleType("bpy")
    mock_bpy.context = MagicMock()
    sys.modules["bpy"] = mock_bpy

    mock_bmesh = types.ModuleType("bmesh")
    sys.modules["bmesh"] = mock_bmesh

    mock_mathutils = types.ModuleType("mathutils")
    mock_mathutils.Vector = _MockVector
    sys.modules["mathutils"] = mock_mathutils

    module_path = os.path.join(
        os.path.dirname(__file__), "..", "addon", "geometry_extractor.py"
    )
    spec = importlib.util.spec_from_file_location("geometry_extractor", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ge = _load_geometry_extractor()


# ──────────────────────────────────────────────────────────────────────
# Helper: mock _compute_mesh_volume and _validate_with_pyvista
# to control auto-detection in unit tests
# ──────────────────────────────────────────────────────────────────────

def _extract_with_forced_detection(mock_ctx, volume_ratio=1.0):
    """
    Run extract_geometry with forced volume ratio.

    volume_ratio=1.0 → box
    volume_ratio=0.785 → cylinder
    volume_ratio=0.524 → sphere
    """
    # Mock _compute_mesh_volume to return a specific ratio
    def mock_volume(obj):
        p_min, p_max = _ge._get_world_bounding_box(obj)
        bb_dims = [p_max[i] - p_min[i] for i in range(3)]
        bb_vol = bb_dims[0] * bb_dims[1] * bb_dims[2]
        return bb_vol * volume_ratio

    # Mock PyVista validation to always confirm
    def mock_validate(obj, candidate):
        return candidate

    with patch.object(_ge, '_compute_mesh_volume', side_effect=mock_volume):
        with patch.object(_ge, '_validate_with_pyvista', side_effect=mock_validate):
            return _ge.extract_geometry(mock_ctx)


# ──────────────────────────────────────────────────────────────────────
# BOX Tests (auto-detected via volume ratio ≈ 1.0)
# ──────────────────────────────────────────────────────────────────────

def test_box_identity():
    """Unit cube at origin → auto-detected as box."""
    obj = _make_mock_object("Cube", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "BOX", "cells": [10, 10, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "box"
    assert result["blocks"][0]["p_min"] == [-1, -1, -1]
    assert result["blocks"][0]["p_max"] == [1, 1, 1]


def test_box_translated():
    """Unit cube at (10,10,10) preserves offset."""
    obj = _make_mock_object("Cube_Far", _UNIT_CUBE_BBOX, _MockMatrix((10, 10, 10)),
                             {"block_type": "BOX", "cells": [10, 10, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert result["blocks"][0]["p_min"] == [9, 9, 9]
    assert result["blocks"][0]["p_max"] == [11, 11, 11]


def test_box_with_stl_projection():
    """BOX with STL file set produces stl_projections dict."""
    obj = _make_mock_object("TerrainBox", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "BOX", "cells": [10, 10, 10],
                              "stl_file": "/path/to/terrain.stl",
                              "stl_projection_face": "top"})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert result["blocks"][0]["stl_projections"] == {"top": "terrain.stl"}


# ──────────────────────────────────────────────────────────────────────
# CYLINDER Tests (auto-detected via volume ratio ≈ π/4)
# ──────────────────────────────────────────────────────────────────────

def test_cylinder_detection():
    """Object with volume ratio ≈ π/4 → auto-detected as cylinder."""
    # Use a tall bounding box (cylinder aligned along Z)
    bbox = [
        (-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0),
        (-1, -1, 3), (1, -1, 3), (1, 1, 3), (-1, 1, 3),
    ]
    obj = _make_mock_object("Cyl", bbox, _MockMatrix((0, 0, 0)),
                             {"block_type": "BOX", "cells": [5, 5, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=math.pi/4)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "cylinder"
    assert "axis_pt1" in result["blocks"][0]
    assert "axis_pt2" in result["blocks"][0]
    assert "radius_point" in result["blocks"][0]


def test_sphere_detection():
    """Object with volume ratio ≈ π/6 → auto-detected as sphere."""
    obj = _make_mock_object("Sphere", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "BOX", "cells": [10, 10, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=math.pi/6)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "sphere"
    assert "center" in result["blocks"][0]
    assert "radius_point" in result["blocks"][0]


def test_infer_cylinder_axis_from_cap_normals():
    """Equal bbox dimensions should still recover the real cylinder axis."""
    vertices = [
        [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0],
        [1, 0, 2], [-1, 0, 2], [0, 1, 2], [0, -1, 2],
    ]
    normals = [
        [0, 0, 1],
        [0, 0, -1],
        [1, 0, 0],
        [-1, 0, 0],
    ]
    areas = [3.1, 3.1, 1.0, 1.0]

    pt1, pt2, radius_point, radius = _ge._infer_cylinder_local_frame(
        vertices,
        normals,
        areas,
    )

    assert round(pt1[2], 6) == 0.0
    assert round(pt2[2], 6) == 2.0
    assert round(radius, 6) == 1.0
    assert round(radius_point[2], 6) == 0.0


def test_unsupported_warning_is_reported():
    """Unsupported auto-detected meshes are kept in warnings and spec output."""
    obj = _make_mock_object("WeirdMesh", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "BOX", "cells": [10, 10, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    with patch.object(_ge, '_compute_mesh_volume', return_value=0.2):
        with patch.object(_ge, '_validate_with_pyvista', return_value="unsupported"):
            result = _ge.extract_geometry(mock_ctx)

    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "unsupported"
    assert result["warnings"]
    assert "WeirdMesh" in result["warnings"][0]


# ──────────────────────────────────────────────────────────────────────
# Dispatch / General Tests
# ──────────────────────────────────────────────────────────────────────

def test_all_mesh_objects_auto_included():
    """All mesh objects are processed."""
    box1 = _make_mock_object("Box1", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "BOX", "cells": [10, 10, 10],
                              "patch_name": "wall"})
    box2 = _make_mock_object("Box2", _UNIT_CUBE_BBOX, _MockMatrix((5, 0, 0)),
                             {"block_type": "BOX", "cells": [20, 10, 10],
                              "patch_name": "inlet"})

    camera = MagicMock()
    camera.type = 'CAMERA'
    camera.name = 'Camera'

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [box1, box2, camera]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert len(result["blocks"]) == 2


def test_exclude_toggle():
    """Objects with exclude_from_mesh=True are skipped."""
    included = _make_mock_object("IncBox", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                                 {"block_type": "BOX", "cells": [10, 10, 10],
                                  "patch_name": "wall"})
    excluded = _make_mock_object("ExBox", _UNIT_CUBE_BBOX, _MockMatrix((5, 0, 0)),
                                 {"exclude_from_mesh": True, "block_type": "BOX",
                                  "cells": [10, 10, 10]})

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [included, excluded]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["name"] == "IncBox"


def test_empty_scene():
    """Empty scene returns empty blocks list."""
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = []

    result = _ge.extract_geometry(mock_ctx)
    assert result["blocks"] == []
    assert result["merge_tolerance"] == 1e-4


def test_block_type_dispatch_extrude():
    """EXTRUDE type bypasses auto-detection (needs real Blender for face extract)."""
    obj = _make_mock_object("ExtrudePlane", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "EXTRUDE", "cells": [10, 10, 10],
                              "extrude_face_index": 0,
                              "extrude_axis": "Z",
                              "extrude_distance": 1.0})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _ge.extract_geometry(mock_ctx)
    # Block should be skipped (extraction error caught — no real bpy.context)
    assert len(result["blocks"]) == 0


def test_block_type_dispatch_revolve():
    """REVOLVE type bypasses auto-detection (needs real Blender for face extract)."""
    obj = _make_mock_object("RevolvePlane", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "REVOLVE", "cells": [10, 10, 10],
                              "revolve_face_index": 0,
                              "revolve_angle": 90.0,
                              "revolve_axis": "Z",
                              "revolve_origin": (0, 0, 0)})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _ge.extract_geometry(mock_ctx)
    # Block should be skipped (extraction error caught)
    assert len(result["blocks"]) == 0


if __name__ == "__main__":
    test_box_identity()
    test_box_translated()
    test_box_with_stl_projection()
    test_cylinder_detection()
    test_sphere_detection()
    test_infer_cylinder_axis_from_cap_normals()
    test_unsupported_warning_is_reported()
    test_all_mesh_objects_auto_included()
    test_exclude_toggle()
    test_empty_scene()
    test_block_type_dispatch_extrude()
    test_block_type_dispatch_revolve()
    print("\nAll geometry extractor unit tests PASSED!")
