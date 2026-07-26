"""
End-to-end integration tests for the sketch-to-block handoff.

These tests specifically cover the boundary between:
  1. CLASSY_OT_extrude_sketch / CLASSY_OT_revolve_sketch (operators.py)
  2. geometry_extractor.extract_geometry() (geometry_extractor.py)

The bug these catch: operators set obj.classy_block_props.block_type = 'EXTRUDE',
but geometry_extractor's fast-path for sketch objects always called
_build_sketch_spec() regardless of block_type, emitting type='sketch' which
mesh_builder raised ValueError on.

These tests chain BOTH steps together with the same mock object — they mutate
the object state via the operator path, then pass the same object to the
extractor and assert the resulting spec type. Isolated unit tests of each
step missed this because they used independently-constructed fixtures.
"""
import sys
import math
from unittest.mock import MagicMock, patch


# ─────────────────────── MOCK BLENDER ENVIRONMENT ───────────────────────
# Must be set before importing any addon module that touches bpy.

class MockOperator:
    """Real Python class so class bodies using it as base class work."""
    pass


mock_bpy = MagicMock()
mock_bpy.types.Operator = MockOperator
mock_bpy.props.EnumProperty = MagicMock(return_value=None)
mock_bpy.props.FloatProperty = MagicMock(return_value=None)
mock_bpy.props.IntProperty = MagicMock(return_value=None)
sys.modules["bpy"] = mock_bpy
sys.modules["bmesh"] = MagicMock()
sys.modules["gpu"] = MagicMock()
sys.modules["gpu_extras"] = MagicMock()
sys.modules["gpu_extras.batch"] = MagicMock()
sys.modules["mathutils"] = MagicMock()
sys.modules["mathutils.geometry"] = MagicMock()
sys.modules["bpy_extras"] = MagicMock()

import addon.operators as _op
import addon.geometry_extractor as _ge


# ─────────────────────── HELPERS ───────────────────────

def _make_sketch_object(num_pts=4):
    """
    Build a mock Blender CURVE object that mimics a ClassySketch.
    
    The object has:
      - obj.type == 'CURVE'
      - obj["classy_sketch"] == True
      - obj.classy_block_props.block_type initially unset (defaults to 'BOX')
      - obj.data.splines[0].points with num_pts entries
    """
    obj = MagicMock()
    obj.type = "CURVE"

    # Custom property dict
    _custom = {"classy_sketch": True}
    obj.get = lambda key, default=None: _custom.get(key, default)
    obj.__getitem__ = lambda self_inner, key: _custom[key]

    # Spline with num_pts POLY points.
    # Each point's .co must return a list with at least 3 elements so
    # p.co[:3] works correctly in _extract_curve_points.
    pts = []
    for i in range(num_pts):
        pt = MagicMock()
        pt.co = [float(i), 0.0, 0.0, 1.0]   # x, y, z, w
        pts.append(pt)

    spline = MagicMock()
    spline.type = "POLY"
    spline.points = pts
    spline.bezier_points = []

    curve_data = MagicMock()
    curve_data.splines = [spline]
    obj.data = curve_data

    # _extract_curve_points calls obj.evaluated_get(depsgraph).
    # In real Blender this returns the evaluated version of the same object.
    # For our mock, evaluated_get must return an object whose .data is the
    # same curve_data we set above — otherwise we'd get a bare MagicMock.
    obj_eval = MagicMock()
    obj_eval.data = curve_data   # same data object
    obj.evaluated_get = MagicMock(return_value=obj_eval)

    # classy_block_props with a real mutable block_type string
    props = MagicMock()
    props.block_type = "BOX"          # initial state — not yet tagged
    props.exclude_from_mesh = False
    props.patch_name = "defaultWall"
    props.grading_type = "RATIO"
    props.grading = [1.0, 1.0, 1.0]
    props.start_size = 1e-4
    props.end_size = 1e-4
    props.cells = [10, 10, 10]
    props.extrude_axis = "Z"
    props.extrude_distance = 1.0
    props.revolve_angle = 90.0
    props.revolve_axis = "Z"
    props.revolve_origin = (0.0, 0.0, 0.0)
    props.chain_source = ""
    props.stl_file = ""
    props.face_patches = []
    obj.classy_block_props = props

    # matrix_world (identity for simplicity)
    obj.matrix_world = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
    obj.name = "ClassySketch"

    return obj


def _run_extrude_operator(obj):
    """
    Simulate what CLASSY_OT_extrude_sketch.execute() does, exactly.
    This replicates the real operator path rather than calling the mock-registered class.
    """
    op_instance = MagicMock()
    ctx = MagicMock()
    ctx.active_object = obj
    result = _op.CLASSY_OT_extrude_sketch.execute(op_instance, ctx)
    return result, op_instance


def _run_revolve_operator(obj):
    """
    Simulate what CLASSY_OT_revolve_sketch.execute() does, exactly.
    """
    op_instance = MagicMock()
    ctx = MagicMock()
    ctx.active_object = obj
    result = _op.CLASSY_OT_revolve_sketch.execute(op_instance, ctx)
    return result, op_instance


def _run_extractor(obj):
    """
    Run geometry_extractor.extract_geometry() with a scene containing only obj.
    Returns the spec dict for the sketch object, or None if no spec was emitted.
    """
    ctx = MagicMock()
    ctx.scene.objects = [obj]
    result = _ge.extract_geometry(ctx)
    blocks = result["blocks"]
    return blocks[0] if blocks else None


# ─────────────────────── END-TO-END TESTS ───────────────────────

def test_extrude_sketch_end_to_end_produces_extrude_spec():
    """
    THE KEY REGRESSION TEST.

    Full chain:
      1. Create a ClassySketch curve object (4 points, block_type='BOX' initially).
      2. Run CLASSY_OT_extrude_sketch.execute() against it (sets block_type='EXTRUDE').
      3. Run geometry_extractor.extract_geometry() against the SAME, now-mutated object.
      4. Assert spec type is 'extrude', NOT 'sketch'.

    This is the exact handoff that failed in real Blender — the operator set
    block_type='EXTRUDE' but the extractor ignored it and always emitted 'sketch'.
    """
    obj = _make_sketch_object(num_pts=4)
    assert obj.classy_block_props.block_type == "BOX"   # precondition

    # Step 1: run the operator — mutates obj.classy_block_props.block_type
    result, op = _run_extrude_operator(obj)
    assert result == {"FINISHED"}, f"Operator did not finish: {result}"
    assert obj.classy_block_props.block_type == "EXTRUDE", (
        "Operator failed to set block_type to EXTRUDE"
    )

    # Step 2: run the extractor against the mutated object
    spec = _run_extractor(obj)

    assert spec is not None, "Extractor emitted no spec for the sketch object"
    assert spec["type"] == "extrude", (
        f"Expected spec type 'extrude', got '{spec['type']}'. "
        "Fast-path in extract_geometry() is probably ignoring block_type."
    )
    assert "face" in spec, "Extrude spec missing 'face' key"
    assert len(spec["face"]) == 4, f"Extrude face should have 4 pts, got {len(spec['face'])}"
    assert "extrude_vector" in spec, "Extrude spec missing 'extrude_vector'"


def test_revolve_sketch_end_to_end_produces_revolve_spec():
    """
    THE KEY REGRESSION TEST — revolve variant.

    Full chain:
      1. Create a ClassySketch curve object (4 points, block_type='BOX').
      2. Run CLASSY_OT_revolve_sketch.execute() (sets block_type='REVOLVE').
      3. Run extract_geometry() against the SAME mutated object.
      4. Assert spec type is 'revolve', NOT 'sketch'.
    """
    obj = _make_sketch_object(num_pts=4)
    assert obj.classy_block_props.block_type == "BOX"   # precondition

    result, op = _run_revolve_operator(obj)
    assert result == {"FINISHED"}, f"Operator did not finish: {result}"
    assert obj.classy_block_props.block_type == "REVOLVE", (
        "Operator failed to set block_type to REVOLVE"
    )

    spec = _run_extractor(obj)

    assert spec is not None, "Extractor emitted no spec for the sketch object"
    assert spec["type"] == "revolve", (
        f"Expected spec type 'revolve', got '{spec['type']}'. "
        "Fast-path in extract_geometry() is probably ignoring block_type."
    )
    assert "face" in spec, "Revolve spec missing 'face' key"
    assert len(spec["face"]) == 4, f"Revolve face should have 4 pts, got {len(spec['face'])}"
    assert "angle_deg" in spec, "Revolve spec missing 'angle_deg'"
    assert "axis" in spec, "Revolve spec missing 'axis'"
    assert "origin" in spec, "Revolve spec missing 'origin'"


def test_untagged_sketch_still_produces_sketch_spec():
    """
    An untagged sketch (block_type not changed by any operator) should still
    emit type='sketch' — the fallback branch must continue to work.
    """
    obj = _make_sketch_object(num_pts=4)
    # Do NOT run any tagging operator — block_type stays 'BOX'

    spec = _run_extractor(obj)

    # An untagged sketch still emits, but as type 'sketch'
    # (It won't be built by mesh_builder — that's intentional, the user
    #  hasn't told us what to do with it yet.)
    assert spec is not None, "Extractor emitted no spec for untagged sketch"
    assert spec["type"] == "sketch", (
        f"Expected untagged sketch to emit type='sketch', got '{spec['type']}'"
    )


def test_extrude_sketch_with_wrong_point_count_emits_unsupported():
    """
    A sketch with != 4 points tagged for EXTRUDE should emit type='unsupported'
    from _build_extrude_spec (not crash), matching the existing behavior in
    _build_extrude_spec's validation path.
    """
    obj = _make_sketch_object(num_pts=3)  # wrong count

    result, op = _run_extrude_operator(obj)
    assert result == {"FINISHED"}
    assert obj.classy_block_props.block_type == "EXTRUDE"

    # The operator warns but doesn't abort. The extractor should emit 'unsupported'.
    spec = _run_extractor(obj)

    assert spec is not None
    assert spec["type"] == "unsupported", (
        f"3-point extrude sketch should emit 'unsupported', got '{spec['type']}'"
    )


def test_revolve_sketch_with_wrong_point_count_emits_unsupported():
    """Revolve variant of the wrong-point-count test."""
    obj = _make_sketch_object(num_pts=5)

    result, op = _run_revolve_operator(obj)
    assert result == {"FINISHED"}
    assert obj.classy_block_props.block_type == "REVOLVE"

    spec = _run_extractor(obj)

    assert spec is not None
    assert spec["type"] == "unsupported", (
        f"5-point revolve sketch should emit 'unsupported', got '{spec['type']}'"
    )
