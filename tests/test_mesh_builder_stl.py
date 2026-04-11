# tests/test_mesh_builder_stl.py
import pytest
import os
import importlib.util
import classy_blocks as cb

_mb_path = os.path.join(os.path.dirname(__file__), "..", "addon", "mesh_builder.py")
_spec = importlib.util.spec_from_file_location("mesh_builder", _mb_path)
_mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mb)

def test_build_box_block_with_stl():
    mesh = cb.Mesh()
    spec = {
        "type": "box",
        "name": "test_box",
        "p_min": [0, 0, 0],
        "p_max": [1, 1, 1],
        "cells": [10, 10, 10],
        "grading_type": "RATIO",
        "grading": [1.0, 1.0, 1.0],
        "stl_projections": {
            "top": "terrain.stl"
        }
    }
    # Should run without error
    _mb.build_box_block_with_stl(mesh, spec)
    
    # We do NOT inspect mesh.blocks directly here as the mesh is unassembled.

def test_build_from_spec_routing(tmp_path):
    output_path = tmp_path / "system" / "blockMeshDict"
    os.makedirs(output_path.parent, exist_ok=True)
    
    spec = {
        "blocks": [
            {
                "type": "box",
                "name": "stl_box",
                "p_min": [0, 0, 0],
                "p_max": [1, 1, 1],
                "cells": [10, 10, 10],
                "stl_projections": {
                    "top": "terrain.stl"
                }
            }
        ],
        "merge_tolerance": 1e-4
    }
    
    _mb.build_from_spec(spec, str(output_path))
    assert output_path.exists()
    
    content = output_path.read_text()
    assert "project" in content
    assert "terrain.stl" in content
