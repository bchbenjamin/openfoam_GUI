import os
import sys
import importlib.util
from unittest.mock import MagicMock
import pytest

sys.path.insert(0, os.path.dirname(__file__))
from _cb_compat import cb

# Mock Blender environment for operators.py
class MockOperator:
    """ """
    pass

mock_bpy = MagicMock()
mock_bpy.types.Operator = MockOperator
sys.modules["bpy"] = mock_bpy

mock_bmesh = MagicMock()
sys.modules["bmesh"] = mock_bmesh

# Also need to mock gpu and gpu_extras if any modules in addon try to import them
mock_gpu = MagicMock()
sys.modules["gpu"] = mock_gpu
mock_gpu_extras = MagicMock()
sys.modules["gpu_extras"] = mock_gpu_extras
sys.modules["gpu_extras.batch"] = mock_gpu_extras
sys.modules["mathutils"] = MagicMock()
sys.modules["mathutils.geometry"] = MagicMock()
sys.modules["bpy_extras"] = MagicMock()

import addon.operators as _op

# Load mesh_builder.py
import addon.mesh_builder as _mb

def test_operator_valid_4_point_sketch() -> None:
    """Valid 4-point sketch sets the block type to EXTRUDE and logs INFO."""
    op_instance = MagicMock()
    
    mock_context = MagicMock()
    mock_obj = MagicMock()
    mock_obj.type = 'CURVE'
    
    mock_curve = MagicMock()
    mock_spline = MagicMock()
    mock_spline.type = 'POLY'
    mock_spline.points = [1, 2, 3, 4]  # 4 points
    mock_curve.splines = [mock_spline]
    mock_obj.data = mock_curve
    
    mock_context.active_object = mock_obj
    
    result = _op.CLASSY_OT_extrude_sketch.execute(op_instance, mock_context)
    
    assert result == {'FINISHED'}
    assert mock_obj.classy_block_props.block_type == 'EXTRUDE'
    op_instance.report.assert_called_with({'INFO'}, "Sketch tagged for Extrusion")

def test_operator_invalid_5_point_sketch() -> None:
    """Invalid 5-point sketch logs a WARNING but still sets block type (no crash)."""
    op_instance = MagicMock()
    
    mock_context = MagicMock()
    mock_obj = MagicMock()
    mock_obj.type = 'CURVE'
    
    mock_curve = MagicMock()
    mock_spline = MagicMock()
    mock_spline.type = 'POLY'
    mock_spline.points = [1, 2, 3, 4, 5]  # 5 points
    mock_curve.splines = [mock_spline]
    mock_obj.data = mock_curve
    
    mock_context.active_object = mock_obj
    
    result = _op.CLASSY_OT_extrude_sketch.execute(op_instance, mock_context)
    
    assert result == {'FINISHED'}
    assert mock_obj.classy_block_props.block_type == 'EXTRUDE'
    op_instance.report.assert_called_with({'WARNING'}, "Sketch has 5 points. Extrude requires exactly 4 points.")

def test_mesh_builder_consumes_spec_without_error(tmp_path) -> None:
    """spec dict from a sketch is consumed without error by mesh_builder.build_from_spec()

    Args:
      tmp_path: 

    Returns:

    """
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)
    
    spec = {
        "blocks": [{
            "type": "extrude",
            "name": "sketch_extrude",
            "face": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
            "extrude_vector": [0, 0, 2],
            "cells": [5, 5, 10],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }],
        "merge_tolerance": 1e-4,
    }
    
    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert "hex" in content
