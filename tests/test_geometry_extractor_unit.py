# tests/test_geometry_extractor_unit.py
# Unit tests for the pure-Python parts of geometry_extractor.py.
#
# These tests mock bpy to verify the spec dict construction logic
# WITHOUT a running Blender instance.
#
# HOW TO RUN:
#   cd ~/classy_blender_mesh
#   python3 -m pytest tests/test_geometry_extractor_unit.py -v
#
# WHAT IS TESTED:
#   1. _get_world_bounding_box — correct min/max from known matrices
#   2. _extract_box — spec dict structure and coordinate preservation
#   3. extract_geometry — dispatch logic, skipping non-block objects
#   4. Safe property access — missing properties default correctly

import sys
import os
import math
import types
from unittest.mock import MagicMock, patch
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
    """
    Minimal 4x4 Matrix replacement that supports @ Vector.
    Represents a translation-only matrix for simplicity.
    """
    def __init__(self, translation=(0, 0, 0)):
        self._tx, self._ty, self._tz = translation

    def __matmul__(self, other):
        """Apply translation: result = point + translation offset."""
        if isinstance(other, (list, tuple)):
            other = _MockVector(other)
        return _MockVector([
            other[0] + self._tx,
            other[1] + self._ty,
            other[2] + self._tz,
        ])

    def to_3x3(self):
        """Returns a mock 3x3 identity matrix."""
        return _Mock3x3Matrix()


class _Mock3x3Matrix:
    """Mock 3x3 matrix (identity) for local axis extraction."""
    def __matmul__(self, other):
        if isinstance(other, (list, tuple)):
            return _MockVector(other)
        return other


def _make_mock_object(name, bound_box, matrix_world, props_dict=None):
    """
    Creates a mock Blender object with the given bounding box and transform.

    Args:
        name: Object name string.
        bound_box: List of 8 (x,y,z) corners in local space.
        matrix_world: _MockMatrix instance.
        props_dict: Dict of classy_block_props attributes.
    """
    obj = MagicMock()
    obj.name = name
    obj.type = 'MESH'
    obj.bound_box = bound_box
    obj.matrix_world = matrix_world

    if props_dict is not None:
        # Use a simple namespace — getattr naturally returns None for missing attrs
        class _Props:
            pass
        mock_props = _Props()
        for key, value in props_dict.items():
            setattr(mock_props, key, value)
        obj.classy_block_props = mock_props
    else:
        obj.classy_block_props = None

    return obj


# Standard unit cube bounding box (local space, 2x2x2 centered at origin)
_UNIT_CUBE_BBOX = [
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
    (-1, -1,  1), (1, -1,  1), (1, 1,  1), (-1, 1,  1),
]

# Axis-aligned box bounding box (0,0,0) to (2,1,3)
_CUSTOM_BBOX = [
    (0, 0, 0), (2, 0, 0), (2, 1, 0), (0, 1, 0),
    (0, 0, 3), (2, 0, 3), (2, 1, 3), (0, 1, 3),
]


# ──────────────────────────────────────────────────────────────────────
# Load geometry_extractor with mocked bpy
# ──────────────────────────────────────────────────────────────────────

def _load_geometry_extractor():
    """
    Loads geometry_extractor.py with mocked bpy and mathutils modules
    so it can be tested without Blender.
    """
    # Create mock bpy module
    mock_bpy = types.ModuleType("bpy")
    mock_bpy.context = MagicMock()
    sys.modules["bpy"] = mock_bpy

    # Create mock mathutils module with our Vector
    mock_mathutils = types.ModuleType("mathutils")
    mock_mathutils.Vector = _MockVector
    sys.modules["mathutils"] = mock_mathutils

    # Load the module directly from file
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
    """Unit cube at origin with identity transform → p_min=(-1,-1,-1), p_max=(1,1,1)."""
    obj = _make_mock_object("Cube", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)))
    p_min, p_max = _ge._get_world_bounding_box(obj)

    assert p_min == [-1, -1, -1], f"Expected [-1,-1,-1], got {p_min}"
    assert p_max == [1, 1, 1], f"Expected [1,1,1], got {p_max}"


def test_get_world_bounding_box_translated():
    """
    Unit cube translated to (10, 10, 10).
    CRITICAL: Coordinates must preserve the (10,10,10) offset.
    """
    obj = _make_mock_object("Cube_Far", _UNIT_CUBE_BBOX, _MockMatrix((10, 10, 10)))
    p_min, p_max = _ge._get_world_bounding_box(obj)

    assert p_min == [9, 9, 9], f"Expected [9,9,9], got {p_min}"
    assert p_max == [11, 11, 11], f"Expected [11,11,11], got {p_max}"


def test_get_world_bounding_box_custom_shape():
    """Custom box (0,0,0)→(2,1,3) with translation (5, 0, 0) → (5,0,0)→(7,1,3)."""
    obj = _make_mock_object("CustomBox", _CUSTOM_BBOX, _MockMatrix((5, 0, 0)))
    p_min, p_max = _ge._get_world_bounding_box(obj)

    assert p_min == [5, 0, 0], f"Expected [5,0,0], got {p_min}"
    assert p_max == [7, 1, 3], f"Expected [7,1,3], got {p_max}"


def test_extract_box_spec_structure():
    """_extract_box returns a well-formed spec dict."""
    obj = _make_mock_object("TestBox", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)))
    spec = _ge._extract_box(obj, [10, 20, 30], [1.0, 1.5, 2.0], "inlet")

    assert spec["type"] == "box"
    assert spec["name"] == "TestBox"
    assert spec["p_min"] == [-1, -1, -1]
    assert spec["p_max"] == [1, 1, 1]
    assert spec["cells"] == [10, 20, 30]
    assert spec["grading"] == [1.0, 1.5, 2.0]
    assert spec["patch_name"] == "inlet"


def test_extract_box_coordinate_preservation():
    """
    Box at (10, 10, 10) must retain its coordinates — not be reset to origin.
    This is the critical coordinate preservation requirement.
    """
    obj = _make_mock_object("FarBox", _UNIT_CUBE_BBOX, _MockMatrix((10, 10, 10)))
    spec = _ge._extract_box(obj, [5, 5, 5], [1.0, 1.0, 1.0], "wall")

    assert spec["p_min"] == [9, 9, 9], f"Coordinate lost! Got {spec['p_min']}"
    assert spec["p_max"] == [11, 11, 11], f"Coordinate lost! Got {spec['p_max']}"


def test_extract_geometry_dispatch():
    """extract_geometry dispatches box blocks and skips non-blocks."""
    # Create a scene with 3 objects: one box block, one non-block, one camera
    box_obj = _make_mock_object("MyBox", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                                {"is_block": True, "block_type": "box",
                                 "cells": [10, 10, 10], "patch_name": "wall"})

    non_block_obj = _make_mock_object("Floor", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                                      {"is_block": False, "block_type": "box"})

    camera_obj = MagicMock()
    camera_obj.type = 'CAMERA'
    camera_obj.name = 'Camera'

    mock_context = MagicMock()
    mock_context.scene.objects = [box_obj, non_block_obj, camera_obj]

    result = _ge.extract_geometry(mock_context)

    assert len(result["blocks"]) == 1, f"Expected 1 block, got {len(result['blocks'])}"
    assert result["blocks"][0]["name"] == "MyBox"
    assert result["blocks"][0]["type"] == "box"
    assert result["merge_tolerance"] == 1e-4


def test_extract_geometry_unknown_type_skipped():
    """Unknown block type is skipped (logged, not raised)."""
    weird_obj = _make_mock_object("Weird", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                                  {"is_block": True, "block_type": "cylinder",
                                   "cells": [10, 10, 10], "patch_name": "wall"})

    mock_context = MagicMock()
    mock_context.scene.objects = [weird_obj]

    result = _ge.extract_geometry(mock_context)
    assert len(result["blocks"]) == 0, "Unknown type should be skipped"


def test_extract_geometry_multiple_boxes():
    """Multiple box blocks are all extracted with correct coordinates."""
    box1 = _make_mock_object("Box1", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"is_block": True, "block_type": "box",
                              "cells": [10, 10, 10], "patch_name": "wall"})
    box2 = _make_mock_object("Box2", _UNIT_CUBE_BBOX, _MockMatrix((5, 0, 0)),
                             {"is_block": True, "block_type": "box",
                              "cells": [20, 10, 10], "patch_name": "inlet"})

    mock_context = MagicMock()
    mock_context.scene.objects = [box1, box2]

    result = _ge.extract_geometry(mock_context)
    assert len(result["blocks"]) == 2

    b1 = result["blocks"][0]
    b2 = result["blocks"][1]

    assert b1["name"] == "Box1"
    assert b1["p_min"] == [-1, -1, -1]

    assert b2["name"] == "Box2"
    assert b2["p_min"] == [4, -1, -1]  # shifted by (5,0,0)
    assert b2["p_max"] == [6, 1, 1]


def test_safe_property_defaults():
    """Missing grading property defaults to [1.0, 1.0, 1.0]."""
    obj = _make_mock_object("NoGrading", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                            {"is_block": True, "block_type": "box",
                             "cells": [10, 10, 10], "patch_name": "wall"})
    # grading is not set in the props — should default

    mock_context = MagicMock()
    mock_context.scene.objects = [obj]

    result = _ge.extract_geometry(mock_context)
    assert result["blocks"][0]["grading"] == [1.0, 1.0, 1.0]


def test_empty_scene():
    """Empty scene returns empty blocks list."""
    mock_context = MagicMock()
    mock_context.scene.objects = []

    result = _ge.extract_geometry(mock_context)
    assert result["blocks"] == []
    assert result["merge_tolerance"] == 1e-4


if __name__ == "__main__":
    test_get_world_bounding_box_identity()
    test_get_world_bounding_box_translated()
    test_get_world_bounding_box_custom_shape()
    test_extract_box_spec_structure()
    test_extract_box_coordinate_preservation()
    test_extract_geometry_dispatch()
    test_extract_geometry_unknown_type_skipped()
    test_extract_geometry_multiple_boxes()
    test_safe_property_defaults()
    test_empty_scene()
    print("\nAll geometry extractor unit tests PASSED!")
