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

    def normalized(self):
        """Return a unit-length copy of this vector."""
        import math
        length = math.sqrt(sum(v * v for v in self._data))
        if length < 1e-12:
            return _MockVector(self._data)
        return _MockVector([v / length for v in self._data])


class _MockQuaternion:
    def to_axis_angle(self):
        return _MockVector([0, 0, 1]), 0.0

class _MockMatrix:
    """Mock translation matrix."""
    def __init__(self, offset):
        self.offset = offset
        
    def decompose(self):
        return (_MockVector(self.offset), _MockQuaternion(), _MockVector([1, 1, 1]))

    def __matmul__(self, other):
        if isinstance(other, (list, tuple)):
            other = _MockVector(other)
        # Translation only
        return _MockVector([
            other[0] + self.offset[0],
            other[1] + self.offset[1],
            other[2] + self.offset[2],
        ])

    def to_3x3(self):
        """Returns a mock 3x3 identity rotation matrix."""
        return _MockMatrix3x3()


class _MockMatrix3x3:
    """Mock 3x3 identity rotation (no rotation applied)."""
    def __matmul__(self, other):
        if isinstance(other, (list, tuple)):
            other = _MockVector(other)
        # Identity: return vector unchanged
        return _MockVector([other[0], other[1], other[2]])


def _make_mock_object(name, bound_box, matrix_world, props_dict=None):
    """Creates a mock Blender mesh object."""
    obj = MagicMock()
    obj.name = name
    obj.type = 'MESH'
    obj.bound_box = bound_box
    obj.matrix_world = matrix_world
    obj.scale = (1.0, 1.0, 1.0)  # Default: no unapplied transforms

    if props_dict is not None:
        class _Props:
            pass
        mock_props = _Props()
        for key, value in props_dict.items():
            setattr(mock_props, key, value)
        obj.classy_block_props = mock_props
    else:
        obj.classy_block_props = None

    obj.get.return_value = None
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

def _extract_with_forced_detection(context, volume_ratio=1.0):
    """Helper to run extraction."""
    return _ge.extract_geometry(context)


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
    """Unit cube at (10,10,10) preserves offset in transform."""
    obj = _make_mock_object("Cube_Far", _UNIT_CUBE_BBOX, _MockMatrix((10, 10, 10)),
                             {"block_type": "BOX", "cells": [10, 10, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert result["blocks"][0]["p_min"] == [-1, -1, -1]
    assert result["blocks"][0]["transform"]["translate"] == [10, 10, 10]
    assert result["blocks"][0]["p_max"] == [1, 1, 1]


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
    """Object with CYLINDER block type uses cylinder builder."""
    # Use a tall bounding box (cylinder aligned along Z)
    bbox = [
        (-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0),
        (-1, -1, 3), (1, -1, 3), (1, 1, 3), (-1, 1, 3),
    ]
    obj = _make_mock_object("Cyl", bbox, _MockMatrix((0, 0, 0)),
                             {"block_type": "CYLINDER", "cells": [5, 5, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "cylinder"
    
    spec = result["blocks"][0]
    assert spec["axis_pt1"] == [0, 0, 0]
    assert spec["axis_pt2"] == [0, 0, 3]
    assert round(spec["radius"], 6) == 1.0
    assert round(spec["radius_point"][2], 6) == 0.0


def test_sphere_detection():
    """Object with SPHERE block type uses sphere builder."""
    obj = _make_mock_object("Sphere", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "SPHERE", "cells": [10, 10, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "sphere"
    assert "center_point" in result["blocks"][0]
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
                             {"block_type": "UNKNOWN_TYPE", "cells": [10, 10, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

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
    # Block should emit an unsupported block since bmesh is mocked
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "unsupported"


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
    # Block should emit an unsupported block since bmesh is mocked
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "unsupported"


# ──────────────────────────────────────────────────────────────────────
# NEW TESTS: Sphere split_axis, unapplied transforms
# ──────────────────────────────────────────────────────────────────────

def test_sphere_spec_has_split_axis():
    """Sphere spec must include a split_axis field from matrix_world rotation."""
    obj = _make_mock_object("Sphere", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "SPHERE", "cells": [10, 10, 10]})
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]

    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert len(result["blocks"]) == 1
    spec = result["blocks"][0]
    assert spec["type"] == "sphere"
    assert "split_axis" in spec
    # With identity rotation, split_axis should be [0, 0, 1]
    assert abs(spec["split_axis"][0]) < 1e-6
    assert abs(spec["split_axis"][1]) < 1e-6
    assert abs(spec["split_axis"][2] - 1.0) < 1e-6


def test_non_uniform_scale_on_box_is_supported():
    """Box supports non-uniform scale."""
    obj = _make_mock_object("ScaledBox", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "BOX", "cells": [10, 10, 10]})
    obj.scale = (2.0, 3.0, 1.0)
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]
    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "box"
    assert len(result["warnings"]) == 0

def test_non_uniform_scale_on_cylinder_is_unsupported():
    """Cylinder does not support non-uniform scale and is skipped."""
    obj = _make_mock_object("ScaledCylinder", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "CYLINDER", "cells": [10, 10, 10]})
    obj.scale = (2.0, 3.0, 1.0)
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]
    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "unsupported"
    assert len(result["warnings"]) == 1
    assert "does not support non-uniform scaling" in result["warnings"][0]

def test_uniform_scale_is_supported():
    """Uniform scale is fully supported on all shapes."""
    obj = _make_mock_object("UniformCylinder", _UNIT_CUBE_BBOX, _MockMatrix((0, 0, 0)),
                             {"block_type": "CYLINDER", "cells": [10, 10, 10]})
    obj.scale = (2.0, 2.0, 2.0)
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]
    result = _extract_with_forced_detection(mock_ctx, volume_ratio=1.0)
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "cylinder"
    assert len(result["warnings"]) == 0

def test_normalize_winding_corrects_inside_out():
    """_normalize_winding should reverse face points if normal opposes sweep vector."""
    # A simple square face in XY plane, points CCW if looking from +Z
    # Normal is +Z
    face_pts_ccw = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    
    # Sweep vector is -Z (opposes normal) -> should reverse
    pts1 = list(face_pts_ccw)
    _ge._normalize_winding(pts1, [0, 0, -1])
    assert pts1 == [[0, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, 0]]
    
    # Sweep vector is +Z (aligns with normal) -> should NOT reverse
    pts2 = list(face_pts_ccw)
    _ge._normalize_winding(pts2, [0, 0, 1])
    assert pts2 == face_pts_ccw

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
    test_sphere_spec_has_split_axis()
    test_non_uniform_scale_on_box_is_supported()
    test_non_uniform_scale_on_cylinder_is_unsupported()
    test_uniform_scale_is_supported()
    print("\nAll geometry extractor unit tests PASSED!")
