# tests/test_vtk_importer_unit.py
# Unit tests for vtk_importer.py pure-Python functions.
#
# Tests _parse_pyvista_faces and find_vtk_files WITHOUT Blender.
# The bpy-dependent functions (load_vtk_as_blender_mesh, _remove_existing_object)
# must be tested inside Blender — see test_steps.md.
#
# HOW TO RUN:
#   cd ~/classy_blender_mesh
#   python3 -m pytest tests/test_vtk_importer_unit.py -v

import os
import sys
import types
import tempfile
import importlib.util
from unittest.mock import MagicMock


# ──────────────────────────────────────────────────────────────────────
# Mock bpy and pyvista BEFORE importing vtk_importer
# ──────────────────────────────────────────────────────────────────────

def _load_vtk_importer():
    """Load vtk_importer.py with mocked bpy so it can run outside Blender."""
    # Mock bpy
    mock_bpy = MagicMock()
    sys.modules["bpy"] = mock_bpy

    # pyvista is real — we have it installed
    # (but we still need bpy mocked for the import to succeed)

    module_path = os.path.join(
        os.path.dirname(__file__), "../..", "addon", "vtk_importer.py"
    )
    spec = importlib.util.spec_from_file_location("vtk_importer", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_vi = _load_vtk_importer()


# ──────────────────────────────────────────────────────────────────────
# Tests for _parse_pyvista_faces
# ──────────────────────────────────────────────────────────────────────

def test_parse_triangles() -> None:
    """Two triangles: [3, 0, 1, 2, 3, 3, 4, 5] → [(0,1,2), (3,4,5)]"""
    raw = [3, 0, 1, 2, 3, 3, 4, 5]
    result = _vi._parse_pyvista_faces(raw)
    assert result == [(0, 1, 2), (3, 4, 5)]


def test_parse_quads() -> None:
    """One quad: [4, 0, 1, 2, 3] → [(0,1,2,3)]"""
    raw = [4, 0, 1, 2, 3]
    result = _vi._parse_pyvista_faces(raw)
    assert result == [(0, 1, 2, 3)]


def test_parse_mixed_tris_and_quads() -> None:
    """Mixed: tri then quad → [(0,1,2), (10,11,12,13)]"""
    raw = [3, 0, 1, 2, 4, 10, 11, 12, 13]
    result = _vi._parse_pyvista_faces(raw)
    assert result == [(0, 1, 2), (10, 11, 12, 13)]


def test_parse_empty() -> None:
    """Empty face array → []"""
    result = _vi._parse_pyvista_faces([])
    assert result == []


def test_parse_single_quad() -> None:
    """Single quad face"""
    raw = [4, 100, 200, 300, 400]
    result = _vi._parse_pyvista_faces(raw)
    assert result == [(100, 200, 300, 400)]


def test_parse_multiple_quads() -> None:
    """Six quads (like a cube surface)"""
    raw = [
        4, 0, 1, 2, 3,
        4, 4, 5, 6, 7,
        4, 0, 1, 5, 4,
        4, 1, 2, 6, 5,
        4, 2, 3, 7, 6,
        4, 3, 0, 4, 7,
    ]
    result = _vi._parse_pyvista_faces(raw)
    assert len(result) == 6
    assert result[0] == (0, 1, 2, 3)
    assert result[5] == (3, 0, 4, 7)


def test_parse_skips_degenerate() -> None:
    """Degenerate faces (n<3) are skipped"""
    raw = [2, 0, 1, 4, 0, 1, 2, 3]  # edge (skip) + quad (keep)
    result = _vi._parse_pyvista_faces(raw)
    assert result == [(0, 1, 2, 3)]


def test_parse_polygon() -> None:
    """Pentagon (n=5) is handled"""
    raw = [5, 0, 1, 2, 3, 4]
    result = _vi._parse_pyvista_faces(raw)
    assert result == [(0, 1, 2, 3, 4)]


def test_parse_numpy_array() -> None:
    """Works with numpy arrays too (as PyVista returns)"""
    import numpy as np
    raw = np.array([4, 0, 1, 2, 3, 3, 4, 5, 6])
    result = _vi._parse_pyvista_faces(raw)
    assert result == [(0, 1, 2, 3), (4, 5, 6)]


# ──────────────────────────────────────────────────────────────────────
# Tests for find_vtk_files
# ──────────────────────────────────────────────────────────────────────

def test_find_vtk_files_empty() -> None:
    """No VTK files → empty list"""
    with tempfile.TemporaryDirectory() as td:
        result = _vi.find_vtk_files(td)
        assert result == []


def test_find_vtk_files_flat() -> None:
    """VTK files directly in VTK/ folder"""
    with tempfile.TemporaryDirectory() as td:
        vtk_dir = os.path.join(td, "VTK")
        os.makedirs(vtk_dir)
        # Create dummy files
        for name in ["internal.vtu", "mesh_0.vtk"]:
            open(os.path.join(vtk_dir, name), "w").close()

        result = _vi.find_vtk_files(td)
        assert len(result) == 2
        assert any("internal.vtu" in f for f in result)
        assert any("mesh_0.vtk" in f for f in result)


def test_find_vtk_files_nested() -> None:
    """VTK files in subdirectory of VTK/"""
    with tempfile.TemporaryDirectory() as td:
        sub_dir = os.path.join(td, "VTK", "cube_test")
        os.makedirs(sub_dir)
        open(os.path.join(sub_dir, "cube_test_0.vtu"), "w").close()

        result = _vi.find_vtk_files(td)
        assert len(result) == 1
        assert "cube_test_0.vtu" in result[0]


def test_find_vtk_files_no_vtk_dir() -> None:
    """Case exists but no VTK/ subfolder → empty list"""
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "system"))  # has system/ but no VTK/
        result = _vi.find_vtk_files(td)
        assert result == []


def test_find_vtk_files_sorted() -> None:
    """Results are sorted alphabetically"""
    with tempfile.TemporaryDirectory() as td:
        vtk_dir = os.path.join(td, "VTK")
        os.makedirs(vtk_dir)
        for name in ["z_last.vtk", "a_first.vtk", "m_middle.vtk"]:
            open(os.path.join(vtk_dir, name), "w").close()

        result = _vi.find_vtk_files(td)
        basenames = [os.path.basename(f) for f in result]
        assert basenames == ["a_first.vtk", "m_middle.vtk", "z_last.vtk"]


# ──────────────────────────────────────────────────────────────────────
# Test load_vtk_as_blender_mesh with real PyVista data (mocked bpy)
# ──────────────────────────────────────────────────────────────────────

def test_load_vtk_pyvista_sphere() -> None:
    """Create a sphere VTK, load it, verify _parse_pyvista_faces works
    on real PyVista output.

    Args:

    Returns:

    """
    import pyvista as pvt

    with tempfile.TemporaryDirectory() as td:
        vtk_path = os.path.join(td, "sphere.vtk")
        sphere = pvt.Sphere(radius=1.0)
        sphere.save(vtk_path)

        # Read it back and parse faces
        pv_mesh = pvt.read(vtk_path)
        surface = pv_mesh.extract_surface()
        faces = _vi._parse_pyvista_faces(surface.faces)

        assert len(faces) > 0, "Should have parsed faces from sphere"
        assert surface.n_points > 0, "Should have points"
        # All faces should be triangles for a sphere
        assert all(len(f) == 3 for f in faces), "Sphere faces should all be triangles"


if __name__ == "__main__":
    test_parse_triangles()
    test_parse_quads()
    test_parse_mixed_tris_and_quads()
    test_parse_empty()
    test_parse_single_quad()
    test_parse_multiple_quads()
    test_parse_skips_degenerate()
    test_parse_polygon()
    test_parse_numpy_array()
    test_find_vtk_files_empty()
    test_find_vtk_files_flat()
    test_find_vtk_files_nested()
    test_find_vtk_files_no_vtk_dir()
    test_find_vtk_files_sorted()
    test_load_vtk_pyvista_sphere()
    print("\nAll VTK importer unit tests PASSED!")
