# tests/test_case_setup.py
# Tests that setup_incompressible_case() creates all required OF13 files.
#
# HOW TO RUN:
#   cd ~/classy_blender_mesh
#   python3 tests/test_case_setup.py
#
# EXPECTED OUTPUT:
#   Prints success for each file created and lists the case structure.
#   The controlDict should say 'application foamRun' (NOT icoFoam).

import os
import sys
import tempfile
import importlib.util

# Load case_setup directly (bypasses addon/__init__.py which imports bpy)
_cs_path = os.path.join(os.path.dirname(__file__), "..", "addon", "case_setup.py")
_spec = importlib.util.spec_from_file_location("case_setup", _cs_path)
_cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cs)
setup_incompressible_case = _cs.setup_incompressible_case

def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_incompressible_case(
            case_path=tmpdir,
            patch_names=["inlet", "outlet", "topWall", "bottomWall"],
            end_time=0.5,
            delta_t=0.005,
            write_interval=20,
            inlet_velocity=[1.0, 0.0, 0.0],
        )

        print("\nCreated files:")
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, tmpdir)
                size = os.path.getsize(full_path)
                print(f"  {rel_path} ({size} bytes)")

        # Check all expected files exist
        expected = [
            "system/controlDict",
            "system/fvSchemes",
            "system/fvSolution",
            "0/U",
            "0/p",
        ]
        all_ok = True
        for expected_file in expected:
            path = os.path.join(tmpdir, expected_file)
            if os.path.exists(path):
                print(f"  OK  {expected_file}")
            else:
                print(f"  MISSING  {expected_file}")
                all_ok = False

        # Verify the controlDict uses foamRun (not icoFoam)
        ctrl = open(os.path.join(tmpdir, "system/controlDict")).read()
        if "foamRun" in ctrl:
            print("  OK  controlDict uses 'foamRun' (OpenFOAM 13 format)")
        else:
            print("  ERROR  controlDict missing 'foamRun' — wrong OpenFOAM version?")
            all_ok = False

        if all_ok:
            print("\nSUCCESS: All case files created correctly!")
        else:
            print("\nERROR: Some files were not created.")

if __name__ == "__main__":
    main()
