# tests/test_lshaped_duct.py
# Tests that two adjacent blocks are correctly merged.
#
# HOW TO RUN:
#   python3 tests/test_lshaped_duct.py
# EXPECTED OUTPUT:
#   "SUCCESS: L-shaped duct blockMeshDict created"

import os
import sys
import tempfile
import importlib.util

# Load mesh_builder directly (bypasses addon/__init__.py which imports bpy)
_mb_path = os.path.join(os.path.dirname(__file__), "../..", "addon", "mesh_builder.py")
_spec = importlib.util.spec_from_file_location("mesh_builder", _mb_path)
_mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mb)
build_from_spec = _mb.build_from_spec

def test_lshaped_duct() -> None:
    """Creates an L-shaped duct from two adjacent boxes.
    Block 1: horizontal section (0,0,0) to (2,1,1)
    Block 2: vertical section  (1,0,1) to (2,1,3)
    These two blocks share a face at x=1..2, y=0..1, z=1

    Args:

    Returns:

    """
    spec = {
        "blocks": [
            {
                "type": "box",
                "name": "horizontal",
                "p_min": [0, 0, 0],
                "p_max": [2, 1, 1],
                "cells": [20, 10, 10],
                "grading": [1.0, 1.0, 1.0],
                "patch_name": "wall",
            },
            {
                "type": "box",
                "name": "vertical",
                "p_min": [1, 0, 1],
                "p_max": [2, 1, 3],
                "cells": [10, 10, 20],
                "grading": [1.0, 1.0, 1.0],
                "patch_name": "wall",
            },
        ],
        "merge_tolerance": 1e-4,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "blockMeshDict")
        build_from_spec(spec, output_path)

        assert os.path.exists(output_path)
        content = open(output_path).read()

        # The output should mention both blocks
        print(f"SUCCESS: L-shaped duct blockMeshDict created ({os.path.getsize(output_path)} bytes)")
        print("First 5 lines:")
        for i, line in enumerate(content.splitlines()):
            if i < 5:
                print(f"{line}")

if __name__ == "__main__":
    test_lshaped_duct()
