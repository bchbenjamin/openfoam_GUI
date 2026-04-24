# tests/test_geometry_extractor_unit.py
# Unit tests for geometry_extractor.py — box/extrude/revolve dispatch.
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
# BOX Tests
# ──────────────────────────────────────────────────────────────────────

def test_box_identity():
    """Unit cube at origin → p_min=(-1,-1,-1), p_max=(1,1,1)."""
    obj = _make_mock_object("Cube", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "BOX", "cells": [10, 10, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _ge.extract_geometry(mock_ctx)
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

    result = _ge.extract_geometry(mock_ctx)
    assert result["blocks"][0]["p_min"] == [9, 9, 9]
    assert result["blocks"][0]["p_max"] == [11, 11, 11]


def test_box_custom_bbox():
    """Custom box (0,0,0)→(2,1,3) + translation (5,0,0)."""
    obj = _make_mock_object("CustomBox", _CUSTOM_BBOX, _MockMatrix((5, 0, 0)),
                             {"block_type": "BOX", "cells": [5, 5, 5]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _ge.extract_geometry(mock_ctx)
    assert result["blocks"][0]["p_min"] == [5, 0, 0]
    assert result["blocks"][0]["p_max"] == [7, 1, 3]


def test_box_with_stl_projection():
    """BOX with STL file set produces stl_projections dict."""
    obj = _make_mock_object("TerrainBox", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "BOX", "cells": [10, 10, 10],
                              "stl_file": "/path/to/terrain.stl",
                              "stl_projection_face": "top"})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _ge.extract_geometry(mock_ctx)
    assert result["blocks"][0]["stl_projections"] == {"top": "terrain.stl"}


# ──────────────────────────────────────────────────────────────────────
# Dispatch / General Tests
# ──────────────────────────────────────────────────────────────────────

def test_all_mesh_objects_auto_included():
    """All mesh objects are included as blocks by default."""
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

    result = _ge.extract_geometry(mock_ctx)
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

    result = _ge.extract_geometry(mock_ctx)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["name"] == "IncBox"


def test_default_properties():
    """Missing props default correctly."""
    obj = _make_mock_object("NoProps", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             props_dict=None)

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _ge.extract_geometry(mock_ctx)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "box"
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


def test_block_type_dispatch_extrude():
    """EXTRUDE type is dispatched correctly (will fail at face extraction
    without full Blender, but the dispatch itself should try)."""
    obj = _make_mock_object("ExtrudePlane", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "EXTRUDE", "cells": [10, 10, 10],
                              "extrude_face_index": 0,
                              "extrude_axis": "Z",
                              "extrude_distance": 1.0})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    # This will fail because _extract_face_vertices_world needs real bpy.context
    # but we verify the error is caught gracefully (not a crash)
    result = _ge.extract_geometry(mock_ctx)
    # Block should be skipped (extraction error caught)
    assert len(result["blocks"]) == 0


def test_block_type_dispatch_revolve():
    """REVOLVE type is dispatched correctly (graceful failure without Blender)."""
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
    test_box_custom_bbox()
    test_box_with_stl_projection()
    test_all_mesh_objects_auto_included()
    test_exclude_toggle()
    test_default_properties()
    test_empty_scene()
    test_block_type_dispatch_extrude()
    test_block_type_dispatch_revolve()
    print("\nAll geometry extractor unit tests PASSED!")
