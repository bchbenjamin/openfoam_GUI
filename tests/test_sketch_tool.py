import sys
import os
import types
from unittest.mock import MagicMock
import importlib.util

# ──────────────────────────────────────────────────────────────────────
# Mock dependencies BEFORE importing geometry_extractor
# ──────────────────────────────────────────────────────────────────────

class _MockVector:
    def __init__(self, data):
        self._data = list(data)
        self.x = self._data[0] if len(self._data) > 0 else 0.0
        self.y = self._data[1] if len(self._data) > 1 else 0.0
        self.z = self._data[2] if len(self._data) > 2 else 0.0

    def __getitem__(self, idx):
        return self._data[idx]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)


def _load_geometry_extractor():
    mock_bpy = types.ModuleType("bpy")
    mock_bpy.context = MagicMock()
    # Provide evaluated_depsgraph_get
    mock_bpy.context.evaluated_depsgraph_get.return_value = MagicMock()
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
# Tests
# ──────────────────────────────────────────────────────────────────────

def test_sketch_fast_path():
    """Verify that an object tagged with classy_sketch bypasses heuristics and extracts properly."""
    # Create mock object
    obj = MagicMock()
    obj.name = "TestSketch"
    obj.type = 'CURVE'
    
    mock_loc = MagicMock()
    mock_loc.x, mock_loc.y, mock_loc.z = 0.0, 0.0, 0.0
    mock_scale = MagicMock()
    mock_scale.x, mock_scale.y, mock_scale.z = 1.0, 1.0, 1.0
    mock_axis = MagicMock()
    mock_axis.x, mock_axis.y, mock_axis.z = 0.0, 0.0, 1.0
    mock_rot = MagicMock()
    mock_rot.to_axis_angle.return_value = (mock_axis, 0.0)
    mock_matrix = MagicMock()
    mock_matrix.decompose.return_value = (mock_loc, mock_rot, mock_scale)
    obj.matrix_world = mock_matrix
    
    # Tag it for the fast path
    def _mock_get(key, default=None):
        if key == "classy_sketch":
            return True
        if key == "classy_curve_type":
            return "POLY"
        return default
    obj.get = _mock_get
    
    # Mock properties to prevent AttributeError
    class _Props:
        exclude_from_mesh = False
        patch_name = "sketchPatch"
        grading_type = "RATIO"
        grading = (1.0, 1.0, 1.0)
        chain_source = ""
        chain_length = 1.0
        chain_radius_2 = 0.0
    obj.classy_block_props = _Props()

    # Mock the curve points
    obj_eval = MagicMock()
    curve_data = MagicMock()
    spline = MagicMock()
    spline.type = 'POLY'
    
    pt1, pt2, pt3 = MagicMock(), MagicMock(), MagicMock()
    pt1.co = [0.0, 0.0, 0.0]
    pt2.co = [1.0, 2.0, 0.0]
    pt3.co = [1.0, 2.0, 3.0]
    spline.points = [pt1, pt2, pt3]
    
    curve_data.splines = [spline]
    obj_eval.data = curve_data
    obj.evaluated_get.return_value = obj_eval

    # Run extraction
    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]
    
    result = _ge.extract_geometry(mock_ctx)
    print(result.get("warnings", []))
    
    assert len(result["blocks"]) == 1
    spec = result["blocks"][0]
    
    assert spec["type"] == "sketch"
    assert spec["name"] == "TestSketch"
    assert spec["curve_type"] == "POLY"
    assert spec["patch_name"] == "sketchPatch"
    
    # Check point ordering is preserved
    pts = spec["points"]
    assert len(pts) == 3
    assert pts[0] == [0.0, 0.0, 0.0]
    assert pts[1] == [1.0, 2.0, 0.0]
    assert pts[2] == [1.0, 2.0, 3.0]

def test_sketch_bezier_extraction():
    """Verify that bezier curves extract bezier_points."""
    # Create mock object
    obj = MagicMock()
    obj.name = "BezierSketch"
    obj.type = 'CURVE'
    
    mock_loc = MagicMock()
    mock_loc.x, mock_loc.y, mock_loc.z = 0.0, 0.0, 0.0
    mock_scale = MagicMock()
    mock_scale.x, mock_scale.y, mock_scale.z = 1.0, 1.0, 1.0
    mock_axis = MagicMock()
    mock_axis.x, mock_axis.y, mock_axis.z = 0.0, 0.0, 1.0
    mock_rot = MagicMock()
    mock_rot.to_axis_angle.return_value = (mock_axis, 0.0)
    mock_matrix = MagicMock()
    mock_matrix.decompose.return_value = (mock_loc, mock_rot, mock_scale)
    obj.matrix_world = mock_matrix
    
    def _mock_get(key, default=None):
        if key == "classy_sketch":
            return True
        if key == "classy_curve_type":
            return "BEZIER"
        return default
    obj.get = _mock_get
    
    class _Props:
        exclude_from_mesh = False
        patch_name = "sketchPatch"
        grading_type = "RATIO"
        grading = (1.0, 1.0, 1.0)
        chain_source = ""
        chain_length = 1.0
        chain_radius_2 = 0.0
    obj.classy_block_props = _Props()

    obj_eval = MagicMock()
    curve_data = MagicMock()
    spline = MagicMock()
    spline.type = 'BEZIER'
    
    pt1, pt2 = MagicMock(), MagicMock()
    pt1.co = [5.0, 5.0, 5.0]
    pt2.co = [-1.0, -2.0, -3.0]
    spline.bezier_points = [pt1, pt2]
    
    curve_data.splines = [spline]
    obj_eval.data = curve_data
    obj.evaluated_get.return_value = obj_eval

    mock_ctx = MagicMock()
    mock_ctx.scene.objects = [obj]
    
    result = _ge.extract_geometry(mock_ctx)
    assert len(result["blocks"]) == 1
    spec = result["blocks"][0]
    
    assert spec["curve_type"] == "BEZIER"
    assert len(spec["points"]) == 2
    assert spec["points"][0] == [5.0, 5.0, 5.0]
    assert spec["points"][1] == [-1.0, -2.0, -3.0]
