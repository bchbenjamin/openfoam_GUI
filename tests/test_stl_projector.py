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
_sp_path = os.path.join(os.path.dirname(__file__), "..", "addon", "stl_projector.py")
_spec = importlib.util.spec_from_file_location("stl_projector", _sp_path)
_sp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sp)

# Also load mesh_builder for integration tests
_mb_path = os.path.join(os.path.dirname(__file__), "..", "addon", "mesh_builder.py")
_mb_spec = importlib.util.spec_from_file_location("mesh_builder", _mb_path)
_mb = importlib.util.module_from_spec(_mb_spec)
_mb_spec.loader.exec_module(_mb)

import pyvista as pv
import classy_blocks as cb


# ─────────────────── HELPERS: synthetic STL surfaces ───────────────────


def _make_flat_plane_stl(path, z=0.5, size=10.0):
    """Write a flat plane at height z as an STL file."""
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
    """
    Write a simple pyramid heightfield as an STL.
    Peak at (0, 0, 1.0), base corners at (±2, ±2, 0).
    All faces are triangles.
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
    """
    Write a sine-wave heightfield as an STL.
    z(x,y) = amplitude * sin(pi*x/size) * sin(pi*y/size)
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

    def test_load_valid_stl(self, tmp_path):
        """load_stl succeeds on a valid STL file."""
        stl_path = _make_flat_plane_stl(str(tmp_path / "plane.stl"))
        surface = _sp.load_stl(stl_path)
        assert surface.n_points > 0
        assert surface.n_cells > 0

    def test_load_nonexistent_raises(self):
        """load_stl raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            _sp.load_stl("/nonexistent/path/terrain.stl")

    def test_load_malformed_raises(self, tmp_path):
        """load_stl raises ValueError for a non-STL file."""
        bad_path = str(tmp_path / "garbage.stl")
        with open(bad_path, "w") as f:
            f.write("this is not an STL file\n")
        with pytest.raises((ValueError, Exception)):
            _sp.load_stl(bad_path)

    def test_load_empty_raises(self, tmp_path):
        """load_stl raises ValueError for an empty file."""
        empty_path = str(tmp_path / "empty.stl")
        with open(empty_path, "wb") as f:
            f.write(b"")
        with pytest.raises((ValueError, Exception)):
            _sp.load_stl(empty_path)


# ─────────────────── TEST: validate_stl ───────────────────


class TestValidateStl:

    def test_validate_valid_stl(self, tmp_path):
        """validate_stl returns valid=True for a proper STL."""
        stl_path = _make_flat_plane_stl(str(tmp_path / "plane.stl"))
        result = _sp.validate_stl(stl_path)
        assert result["valid"] is True
        assert result["n_triangles"] > 0
        assert result["error"] is None

    def test_validate_nonexistent_returns_error(self):
        """validate_stl returns valid=False with error for missing file."""
        result = _sp.validate_stl("/nonexistent/terrain.stl")
        assert result["valid"] is False
        assert result["error"] is not None
        assert "not found" in result["error"]

    def test_validate_warns_on_non_manifold(self, tmp_path):
        """validate_stl warns if surface is not manifold."""
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


# ─────────────────── TEST: project_points_to_surface ───────────────────


class TestProjectPointsToSurface:

    def test_project_flat_plane(self, tmp_path):
        """Points projected onto a flat plane at z=0.5 land at z=0.5."""
        stl_path = _make_flat_plane_stl(str(tmp_path / "plane.stl"), z=0.5)
        surface = _sp.load_stl(stl_path)

        points = np.array([
            [0, 0, 2],     # above the plane
            [0.5, 0.5, 3], # above the plane
            [-0.5, -0.5, -1],  # below the plane
        ])

        projected, warnings = _sp.project_points_to_surface(
            points, surface, direction="z"
        )

        assert projected.shape == (3, 3)
        # All z-values should be approximately 0.5
        np.testing.assert_allclose(projected[:, 2], 0.5, atol=0.05)
        # x, y should be preserved
        np.testing.assert_allclose(projected[:, 0], points[:, 0], atol=0.01)
        np.testing.assert_allclose(projected[:, 1], points[:, 1], atol=0.01)

    def test_project_pyramid(self, tmp_path):
        """Points projected onto a pyramid get z values matching the slope."""
        stl_path = _make_pyramid_stl(str(tmp_path / "pyramid.stl"))
        surface = _sp.load_stl(stl_path)

        # Point directly above the peak (0, 0) — should land at z ≈ 1.0
        points = np.array([[0, 0, 5]])
        projected, warnings = _sp.project_points_to_surface(
            points, surface, direction="z"
        )
        assert projected[0, 2] > 0.8  # Should be near peak

    def test_miss_fallback(self, tmp_path):
        """Points outside the surface footprint fall back to nearest point."""
        stl_path = _make_flat_plane_stl(
            str(tmp_path / "small_plane.stl"), z=0.5, size=1.0
        )
        surface = _sp.load_stl(stl_path)

        # Point far outside the 1x1 plane
        points = np.array([[100, 100, 5]])
        projected, warnings = _sp.project_points_to_surface(
            points, surface, direction="z"
        )

        assert len(warnings) > 0
        assert any("fell back" in w or "missed" in w for w in warnings)

    def test_miss_max_distance(self, tmp_path):
        """Points beyond max_distance are left unchanged."""
        stl_path = _make_flat_plane_stl(
            str(tmp_path / "small_plane.stl"), z=0.5, size=1.0
        )
        surface = _sp.load_stl(stl_path)

        far_point = np.array([[100, 100, 5]])
        projected, warnings = _sp.project_points_to_surface(
            far_point, surface, direction="z", max_distance=1.0
        )

        # Point should be left unchanged
        np.testing.assert_allclose(projected, far_point, atol=0.01)
        assert any("Left unchanged" in w for w in warnings)

    def test_invalid_direction_raises(self, tmp_path):
        """Invalid direction string raises ValueError."""
        stl_path = _make_flat_plane_stl(str(tmp_path / "plane.stl"))
        surface = _sp.load_stl(stl_path)

        with pytest.raises(ValueError, match="Unknown direction"):
            _sp.project_points_to_surface(
                np.array([[0, 0, 0]]), surface, direction="q"
            )


# ─────────────────── TEST: project_face_to_stl ───────────────────


class TestProjectFaceToStl:

    def test_box_top_face_projection(self, tmp_path):
        """Projecting a box's top face updates p_max z coordinate."""
        stl_path = _make_flat_plane_stl(
            str(tmp_path / "plane.stl"), z=0.75, size=10.0
        )

        spec = {
            "type": "box",
            "name": "test_box",
            "p_min": [0, 0, 0],
            "p_max": [1, 1, 1],
            "cells": [10, 10, 10],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }

        updated = _sp.project_face_to_stl(spec, "top", stl_path, "z")

        # The top face z-values should be projected to 0.75
        assert updated["p_max"][2] == pytest.approx(0.75, abs=0.05)
        # The bottom should be unchanged
        assert updated["p_min"][2] == pytest.approx(0.0, abs=0.01)
        # Projected metadata should be present
        assert "projected" in updated
        assert "top" in updated["projected"]

    def test_box_invalid_face_raises(self, tmp_path):
        """Unknown face name raises ValueError."""
        stl_path = _make_flat_plane_stl(str(tmp_path / "plane.stl"))
        spec = {
            "type": "box",
            "p_min": [0, 0, 0],
            "p_max": [1, 1, 1],
        }
        with pytest.raises(ValueError, match="Unknown face name"):
            _sp.project_face_to_stl(spec, "invalid_face", stl_path)


# ─────────────────── TEST: integration with mesh_builder ───────────────────


class TestIntegration:

    def test_projected_spec_consumed_by_mesh_builder(self, tmp_path):
        """
        A spec dict produced by project_face_to_stl() can be consumed
        by mesh_builder.build_from_spec() without errors.
        """
        stl_path = _make_flat_plane_stl(
            str(tmp_path / "terrain.stl"), z=0.8, size=10.0
        )

        spec = {
            "type": "box",
            "name": "terrain_box",
            "p_min": [0, 0, 0],
            "p_max": [1, 1, 1],
            "cells": [5, 5, 5],
            "grading_type": "RATIO",
            "grading": [1.0, 1.0, 1.0],
        }

        updated = _sp.project_face_to_stl(spec, "top", stl_path, "z")

        # Build the mesh — should not throw
        output_path = tmp_path / "system" / "blockMeshDict"
        os.makedirs(output_path.parent, exist_ok=True)

        full_spec = {
            "blocks": [updated],
            "merge_tolerance": 1e-4,
        }
        _mb.build_from_spec(full_spec, str(output_path))
        assert output_path.exists()

        content = output_path.read_text()
        assert "hex" in content

    def test_sine_wave_projection_accuracy(self, tmp_path):
        """
        Project box top onto a sine-wave surface and verify z values
        match the analytic function within tolerance.
        """
        amplitude = 0.3
        size = 4.0
        stl_path = _make_sine_wave_stl(
            str(tmp_path / "sine.stl"),
            amplitude=amplitude,
            size=size,
        )
        surface = _sp.load_stl(stl_path)

        # Test points at known positions on the sine wave
        # z(x,y) = 0.3 * sin(pi*x/4) * sin(pi*y/4)
        test_points = np.array([
            [0.0, 0.0, 5.0],  # center: sin(0)*sin(0) = 0
            [1.0, 1.0, 5.0],  # sin(pi/4)*sin(pi/4) ≈ 0.5*0.5 = 0.25 * 0.3
        ])

        projected, warnings = _sp.project_points_to_surface(
            test_points, surface, direction="z"
        )

        # Center point: z should be ≈ 0.0
        assert abs(projected[0, 2]) < 0.1

        # (1,1) point: z ≈ 0.3 * sin(pi/4) * sin(pi/4) ≈ 0.15
        expected_z = amplitude * np.sin(np.pi * 1.0 / size) * np.sin(np.pi * 1.0 / size)
        assert abs(projected[1, 2] - expected_z) < 0.1
