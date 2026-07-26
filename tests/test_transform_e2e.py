import sys
from unittest.mock import MagicMock
import pytest
import math

# Mock Blender modules before import
sys.modules['bpy'] = MagicMock()
sys.modules['bpy_extras'] = MagicMock()
sys.modules['bmesh'] = MagicMock()
sys.modules['mathutils'] = MagicMock()
sys.modules['mathutils.geometry'] = MagicMock()
sys.modules['gpu'] = MagicMock()
sys.modules['gpu_extras'] = MagicMock()
sys.modules['gpu_extras.batch'] = MagicMock()

import classy_blocks as cb
from addon.geometry_extractor import _build_box_spec
from addon.mesh_builder import _build_box

def _make_box_object(name, translate_list, rotate_axis_list, rotate_angle, scale_list):
    """Creates a mock blender object with a mocked matrix_world.decompose()"""
    obj = MagicMock()
    obj.name = name
    obj.type = 'MESH'
    
    # 2x2x2 cube centered at origin locally
    obj.bound_box = [
        [-1, -1, -1], [1, -1, -1], [-1, 1, -1], [1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [-1, 1, 1], [1, 1, 1]
    ]
    
    # Mock matrix_world and decompose
    mock_loc = MagicMock()
    mock_loc.x, mock_loc.y, mock_loc.z = translate_list
    
    mock_scale = MagicMock()
    mock_scale.x, mock_scale.y, mock_scale.z = scale_list
    
    mock_axis = MagicMock()
    mock_axis.x, mock_axis.y, mock_axis.z = rotate_axis_list
    
    mock_rot = MagicMock()
    mock_rot.to_axis_angle.return_value = (mock_axis, rotate_angle)
    
    mock_matrix = MagicMock()
    mock_matrix.decompose.return_value = (mock_loc, mock_rot, mock_scale)
    obj.matrix_world = mock_matrix
    
    props = MagicMock()
    props.cells = [10, 10, 10]
    props.patch_name = "defaultWall"
    props.grading_type = "RATIO"
    props.grading = [1.0, 1.0, 1.0]
    props.start_size = 1e-4
    props.end_size = 1e-4
    
    return obj, props

def test_box_translation_and_rotation_applied_to_mesh():
    """
    Ensures a box with translation and rotation correctly outputs
    transformed coordinates via the pipeline.
    """
    obj, props = _make_box_object(
        "TestBox", 
        translate_list=[5.0, 0.0, 0.0], 
        rotate_axis_list=[0.0, 0.0, 1.0], 
        rotate_angle=math.pi/2, # 90 deg around Z
        scale_list=[1.0, 1.0, 1.0]
    )
    
    spec = _build_box_spec(obj, props)
    assert "transform" in spec
    assert spec["transform"]["translate"][0] == pytest.approx(5.0)
    
    mesh = cb.Mesh()
    _build_box(mesh, spec)
    
    assert len(mesh.operations) == 1
    box = mesh.operations[0]
    
    center = box.center
    assert center[0] == pytest.approx(5.0)
    assert center[1] == pytest.approx(0.0)
    assert center[2] == pytest.approx(0.0)
    
    pts = []
    pts = box.point_array
        
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    
    # After +90deg Z rot, X limits are bounds on Y, etc.
    # Center is 5,0,0. Dimensions are 2x2.
    assert min(xs) == pytest.approx(4.0)
    assert max(xs) == pytest.approx(6.0)
    assert min(ys) == pytest.approx(-1.0)
    assert max(ys) == pytest.approx(1.0)

def test_box_non_uniform_scale_applied_to_mesh():
    """
    Ensures a box with non-uniform scale preserves all 3 axes
    and correctly outputs scaled coordinates.
    """
    obj, props = _make_box_object(
        "ScaledBox", 
        translate_list=[0.0, 0.0, 0.0], 
        rotate_axis_list=[0.0, 0.0, 1.0], 
        rotate_angle=0.0,
        scale_list=[2.0, 3.0, 0.5]
    )
    
    spec = _build_box_spec(obj, props)
    assert "transform" in spec
    scale_spec = spec["transform"]["scale"]
    assert scale_spec[0] == pytest.approx(2.0)
    assert scale_spec[1] == pytest.approx(3.0)
    assert scale_spec[2] == pytest.approx(0.5)
    
    mesh = cb.Mesh()
    _build_box(mesh, spec)
    
    assert len(mesh.operations) == 1
    box = mesh.operations[0]
    pts = []
    pts = box.point_array
        
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    
    # Original bounds [-1, 1]. Scaled by (2, 3, 0.5)
    assert min(xs) == pytest.approx(-2.0)
    assert max(xs) == pytest.approx(2.0)
    assert min(ys) == pytest.approx(-3.0)
    assert max(ys) == pytest.approx(3.0)
    assert min(zs) == pytest.approx(-0.5)
    assert max(zs) == pytest.approx(0.5)
