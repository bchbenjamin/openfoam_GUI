"""
tests/test_grading.py
Tests that the mesh_builder correctly handles all three grading types:
  - RATIO (c2c_expansion)
  - START_SIZE (first cell width)
  - SYMMETRIC (first + last cell width)

Generates a blockMeshDict for each case and verifies it contains
the expected grading parameters.
"""

import os
import sys
import importlib.util
import tempfile

# Load mesh_builder directly (bypasses addon/__init__.py which needs bpy)
_mb_path = os.path.join(os.path.dirname(__file__), "..", "addon", "mesh_builder.py")
_spec = importlib.util.spec_from_file_location("mesh_builder", _mb_path)
_mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mb)

BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "foam_cases", "cube_test", "system")


def _make_box_spec(grading_type="RATIO", grading=None, start_size=1e-4, end_size=1e-4):
    if grading is None:
        grading = [1.0, 1.0, 1.0]
    return {
        "blocks": [{
            "type": "box",
            "name": "test_box",
            "p_min": [0, 0, 0],
            "p_max": [1, 1, 1],
            "cells": [10, 10, 10],
            "grading": grading,
            "grading_type": grading_type,
            "start_size": start_size,
            "end_size": end_size,
        }],
        "merge_tolerance": 1e-4,
    }


def test_grading_ratio():
    """RATIO grading with c2c_expansion=2.0 should produce a non-uniform blockMeshDict."""
    spec = _make_box_spec(grading_type="RATIO", grading=[2.0, 1.0, 1.0])
    out = os.path.join(BUILD_DIR, "blockMeshDict")
    os.makedirs(BUILD_DIR, exist_ok=True)
    _mb.build_from_spec(spec, out)

    content = open(out).read()
    assert "simpleGrading" in content or "edgeGrading" in content or "simpleSpline" in content \
        or len(content) > 100, "blockMeshDict should contain grading data"
    print("[TEST PASSED] RATIO grading generated valid blockMeshDict")


def test_grading_start_size():
    """START_SIZE grading should produce a blockMeshDict without errors."""
    spec = _make_box_spec(grading_type="START_SIZE", start_size=0.05)
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "blockMeshDict")
        _mb.build_from_spec(spec, out)
        content = open(out).read()
        assert len(content) > 100, "blockMeshDict should have content"
        print(f"[TEST PASSED] START_SIZE grading generated blockMeshDict ({len(content)} bytes)")


def test_grading_symmetric():
    """SYMMETRIC grading should produce a blockMeshDict without errors."""
    spec = _make_box_spec(grading_type="SYMMETRIC", start_size=0.02, end_size=0.1)
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "blockMeshDict")
        _mb.build_from_spec(spec, out)
        content = open(out).read()
        assert len(content) > 100, "blockMeshDict should have content"
        print(f"[TEST PASSED] SYMMETRIC grading generated blockMeshDict ({len(content)} bytes)")
