# tests/test_stl_projector.py
# Unit and integration tests for addon/stl_projector.py.
#
# Uses the importlib.util direct-load pattern (per DEV_NOTES.md) to bypass
# addon/__init__.py which requires bpy.
import pytest
import os
import importlib.util
import tempfile
import numpy as np

os.environ.setdefault("NUMBA_DISABLE_JIT", "1")

# Direct-load stl_projector.py without touching __init__.py
_sp_path = os.path.join(os.path.dirname(__file__), "../..", "addon", "stl_projector.py")
_spec = importlib.util.spec_from_file_location("stl_projector", _sp_path)
_sp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sp)

# Also load mesh_builder for integration tests
_mb_path = os.path.join(os.path.dirname(__file__), "../..", "addon", "mesh_builder.py")
_mb_spec = importlib.util.spec_from_file_location("mesh_builder", _mb_path)
_mb = importlib.util.module_from_spec(_mb_spec)
_mb_spec.loader.exec_module(_mb)

import pyvista as pv
import classy_blocks as cb


# ─────────────────── HELPERS: synthetic STL surfaces ───────────────────


def _make_flat_plane_stl(path, z=0.5, size=10.0):
    """Write a flat plane at height z as an STL file.

    Args:
      path: 
      z:  (Default value = 0.5)
      size:  (Default value = 10.0)

    Returns:

    """
    plane = pv.Plane(
        center=(0, 0, z),
        direction=(0, 0, 1),
        i_size=size,
        j_size=size,
        i_resolution=4,
        j_resolution=4,
    )
    plane.save(path)
    return path


def _make_pyramid_stl(path):
    """Write a simple pyramid heightfield as an STL.
    Peak at (0, 0, 1.0), base corners at (±2, ±2, 0).
    All faces are triangles.

    Args:
      path: 

    Returns:

    """
    points = np.array([
        [-2, -2, 0],  # 0
        [ 2, -2, 0],  # 1
        [ 2,  2, 0],  # 2
        [-2,  2, 0],  # 3
        [ 0,  0, 1],  # 4 (peak)
    ], dtype=float)
    # All triangular faces (VTK format: [n_verts, v0, v1, v2])
    faces = np.hstack([
        [3, 0, 1, 4],  # front slope
        [3, 1, 2, 4],  # right slope
        [3, 2, 3, 4],  # back slope
        [3, 3, 0, 4],  # left slope
        [3, 0, 1, 2],  # base tri 1
        [3, 0, 2, 3],  # base tri 2
    ])
    mesh = pv.PolyData(points, faces)
    mesh.save(path)
    return path


def _make_sine_wave_stl(path, amplitude=0.3, size=4.0, resolution=20):
    """Write a sine-wave heightfield as an STL.
    z(x,y) = amplitude * sin(pi*x/size) * sin(pi*y/size)

    Args:
      path: 
      amplitude:  (Default value = 0.3)
      size:  (Default value = 4.0)
      resolution:  (Default value = 20)

    Returns:

    """
    x = np.linspace(-size/2, size/2, resolution)
    y = np.linspace(-size/2, size/2, resolution)
    xx, yy = np.meshgrid(x, y)
    zz = amplitude * np.sin(np.pi * xx / size) * np.sin(np.pi * yy / size)
    grid = pv.StructuredGrid(xx, yy, zz)
    surface = grid.extract_surface()
    surface.triangulate().save(path)
    return path


# ─────────────────── TEST: load_stl ───────────────────


class TestLoadStl:
    """ """

    def test_load_valid_stl(self, tmp_path) -> None:
        """load_stl succeeds on a valid STL file.

        Args:
          tmp_path: 

        Returns:

        """
        stl_path = _make_flat_plane_stl(str(tmp_path / "plane.stl"))
        surface = _sp.load_stl(stl_path)
        assert surface.n_points > 0
        assert surface.n_cells > 0

    def test_load_nonexistent_raises(self) -> None:
        """load_stl raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            _sp.load_stl("/nonexistent/path/terrain.stl")

    def test_load_malformed_raises(self, tmp_path) -> None:
        """load_stl raises ValueError for a non-STL file.

        Args:
          tmp_path: 

        Returns:

        """
        bad_path = str(tmp_path / "garbage.stl")
        with open(bad_path, "w") as f:
            f.write("this is not an STL file\n")
        with pytest.raises((ValueError, Exception)):
            _sp.load_stl(bad_path)

    def test_load_empty_raises(self, tmp_path) -> None:
        """load_stl raises ValueError for an empty file.

        Args:
          tmp_path: 

        Returns:

        """
        empty_path = str(tmp_path / "empty.stl")
        with open(empty_path, "wb") as f:
            f.write(b"")
        with pytest.raises((ValueError, Exception)):
            _sp.load_stl(empty_path)


# ─────────────────── TEST: validate_stl ───────────────────


class TestValidateStl:
    """ """

    def test_validate_valid_stl(self, tmp_path) -> None:
        """validate_stl returns valid=True for a proper STL.

        Args:
          tmp_path: 

        Returns:

        """
        stl_path = _make_flat_plane_stl(str(tmp_path / "plane.stl"))
        result = _sp.validate_stl(stl_path)
        assert result["valid"] is True
        assert result["n_triangles"] > 0
        assert result["error"] is None

    def test_validate_nonexistent_returns_error(self) -> None:
        """validate_stl returns valid=False with error for missing file."""
        result = _sp.validate_stl("/nonexistent/terrain.stl")
        assert result["valid"] is False
        assert result["error"] is not None
        assert "not found" in result["error"]

    def test_validate_warns_on_non_manifold(self, tmp_path) -> None:
        """validate_stl warns if surface is not manifold.

        Args:
          tmp_path: 

        Returns:

        """
        # A single triangle is not manifold
        pts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
        faces = np.array([3, 0, 1, 2])
        tri = pv.PolyData(pts, faces)
        stl_path = str(tmp_path / "tri.stl")
        tri.save(stl_path)

        result = _sp.validate_stl(stl_path)
        assert result["valid"] is True
        assert result["is_manifold"] is False
        # Should have a non-manifold warning
        assert any("manifold" in w.lower() for w in result["warnings"])



