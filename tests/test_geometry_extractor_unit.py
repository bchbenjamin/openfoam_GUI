# tests/test_geometry_extractor_unit.py
# Unit tests for geometry_extractor.py — universal Box+projection approach.
#
# HOW TO RUN:
#   cd ~/classy_blender_mesh
#   python3 -m pytest tests/test_geometry_extractor_unit.py -v

import sys
import os
import types
from unittest.mock import MagicMock
import importlib.util


# ──────────────────────────────────────────────────────────────────────
# Mock bpy and mathutils BEFORE importing geometry_extractor
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

    def __repr__(self):
        return f"MockVector({self._data})"


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


def _make_mock_object(name, bound_box, matrix_world, props_dict=None,
                      num_verts=None, num_faces=None, all_quads=True):
    """
    Creates a mock Blender mesh object.

    Args:
        num_verts: Override vertex count (for _is_box_shaped testing).
        num_faces: Override face count.
        all_quads: Whether all faces are quads (for box detection).
    """
    obj = MagicMock()
    obj.name = name
    obj.type = 'MESH'
    obj.bound_box = bound_box
    obj.matrix_world = matrix_world

    # Mock mesh data for _is_box_shaped
    actual_verts = num_verts if num_verts is not None else len(bound_box)
    actual_faces = num_faces if num_faces is not None else 6

    mock_verts = [MagicMock() for _ in range(actual_verts)]
    obj.data.vertices = mock_verts

    mock_faces = []
    for _ in range(actual_faces):
        f = MagicMock()
        f.vertices = [0, 1, 2, 3] if all_quads else [0, 1, 2]
        mock_faces.append(f)
    obj.data.polygons = mock_faces

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

_CUSTOM_BBOX = [
    (0, 0, 0), (2, 0, 0), (2, 1, 0), (0, 1, 0),
    (0, 0, 3), (2, 0, 3), (2, 1, 3), (0, 1, 3),
]


# ──────────────────────────────────────────────────────────────────────
# Load geometry_extractor with mocked bpy
# ──────────────────────────────────────────────────────────────────────

def _load_geometry_extractor():
    mock_bpy = types.ModuleType("bpy")
    mock_bpy.context = MagicMock()
    sys.modules["bpy"] = mock_bpy

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
# Tests
# ──────────────────────────────────────────────────────────────────────

def test_get_world_bounding_box_identity():
    """Unit cube at origin → p_min=(-1,-1,-1), p_max=(1,1,1)."""
    obj = _make_mock_object("Cube", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)))
    p_min, p_max = _ge._get_world_bounding_box(obj)
    assert p_min == [-1, -1, -1]
    assert p_max == [1, 1, 1]


def test_get_world_bounding_box_translated():
    """Unit cube at (10,10,10) preserves offset."""
    obj = _make_mock_object("Cube_Far", _UNIT_CUBE_BBOX, _MockMatrix((10, 10, 10)))
    p_min, p_max = _ge._get_world_bounding_box(obj)
    assert p_min == [9, 9, 9]
    assert p_max == [11, 11, 11]


def test_get_world_bounding_box_custom():
    """Custom box (0,0,0)→(2,1,3) + translation (5,0,0)."""
    obj = _make_mock_object("CustomBox", _CUSTOM_BBOX, _MockMatrix((5, 0, 0)))
    p_min, p_max = _ge._get_world_bounding_box(obj)
    assert p_min == [5, 0, 0]
    assert p_max == [7, 1, 3]


def test_all_mesh_objects_auto_included():
    """All mesh objects are included as blocks by default."""
    box1 = _make_mock_object("Box1", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"cells": [10, 10, 10], "patch_name": "wall"})
    box2 = _make_mock_object("Box2", _UNIT_CUBE_BBOX, _MockMatrix((5, 0, 0)),
                             {"cells": [20, 10, 10], "patch_name": "inlet"})

    camera = MagicMock()
    camera.type = 'CAMERA'
    camera.name = 'Camera'

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [box1, box2, camera]

    result = _ge.extract_geometry(mock_ctx)
    assert len(result["blocks"]) == 2
    assert result["blocks"][0]["name"] == "Box1"
    assert result["blocks"][1]["name"] == "Box2"


def test_exclude_toggle():
    """Objects with exclude_from_mesh=True are skipped."""
    included = _make_mock_object("IncBox", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                                 {"cells": [10, 10, 10], "patch_name": "wall"})
    excluded = _make_mock_object("ExBox", _UNIT_CUBE_BBOX, _MockMatrix((5, 0, 0)),
                                 {"exclude_from_mesh": True, "cells": [10, 10, 10]})

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [included, excluded]

    result = _ge.extract_geometry(mock_ctx)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["name"] == "IncBox"


def test_all_blocks_are_type_box():
    """Every block is type 'box' regardless of shape."""
    cube = _make_mock_object("Cube", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                              {"cells": [10, 10, 10]},
                              num_verts=8, num_faces=6, all_quads=True)
    sphere = _make_mock_object("Sphere", _UNIT_CUBE_BBOX, _MockMatrix((5, 0, 0)),
                                {"cells": [10, 10, 10]},
                                num_verts=482, num_faces=480, all_quads=True)

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [cube, sphere]

    result = _ge.extract_geometry(mock_ctx)
    assert len(result["blocks"]) == 2
    assert result["blocks"][0]["type"] == "box"
    assert result["blocks"][1]["type"] == "box"


def test_box_skips_self_projection():
    """A plain cube (8v, 6f, all quads) does NOT need self-projection."""
    cube = _make_mock_object("Cube", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                              {"cells": [10, 10, 10]},
                              num_verts=8, num_faces=6, all_quads=True)

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [cube]

    result = _ge.extract_geometry(mock_ctx)
    assert result["blocks"][0]["needs_self_projection"] == False


def test_nonbox_needs_self_projection():
    """A sphere (482 verts) DOES need self-projection."""
    sphere = _make_mock_object("Sphere", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                                {"cells": [10, 10, 10]},
                                num_verts=482, num_faces=480, all_quads=True)

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [sphere]

    result = _ge.extract_geometry(mock_ctx)
    assert result["blocks"][0]["needs_self_projection"] == True


def test_coordinate_preservation():
    """Coordinates must be preserved at (10,10,10)."""
    obj = _make_mock_object("FarBox", _UNIT_CUBE_BBOX, _MockMatrix((10, 10, 10)),
                             {"cells": [5, 5, 5]})

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _ge.extract_geometry(mock_ctx)
    assert result["blocks"][0]["p_min"] == [9, 9, 9]
    assert result["blocks"][0]["p_max"] == [11, 11, 11]


def test_default_properties():
    """Missing props default correctly."""
    obj = _make_mock_object("NoProps", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             props_dict=None)

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _ge.extract_geometry(mock_ctx)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["cells"] == [10, 10, 10]
    assert result["blocks"][0]["grading"] == [1.0, 1.0, 1.0]
    assert result["blocks"][0]["patch_name"] == "defaultWall"


def test_empty_scene():
    """Empty scene returns empty blocks list."""
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = []

    result = _ge.extract_geometry(mock_ctx)
    assert result["blocks"] == []
    assert result["merge_tolerance"] == 1e-4


if __name__ == "__main__":
    test_get_world_bounding_box_identity()
    test_get_world_bounding_box_translated()
    test_get_world_bounding_box_custom()
    test_all_mesh_objects_auto_included()
    test_exclude_toggle()
    test_all_blocks_are_type_box()
    test_box_skips_self_projection()
    test_nonbox_needs_self_projection()
    test_coordinate_preservation()
    test_default_properties()
    test_empty_scene()
    print("\nAll geometry extractor unit tests PASSED!")
