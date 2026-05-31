# test_load_vtk.py
# Loads the VTK result from foamToVTK and prints mesh statistics.
#
# HOW TO RUN:
#   python3 test_load_vtk.py
#   (run from ~/foam_cases/ after completing Steps 1.1-1.4)
#
# EXPECTED OUTPUT:
#   Mesh statistics including vertex count and bounds

import os
import glob
import pyvista as pv

def load_foam_vtk(case_dir):
    """
    Finds and loads the VTK file produced by foamToVTK.
    foamToVTK creates a subdirectory structure: VTK/internal.vtu or similar.
    """
    case_dir = os.path.expanduser(case_dir)

    # Search for VTK files recursively in the case directory
    vtk_patterns = [
        os.path.join(case_dir, "VTK", "*.vtu"),
        os.path.join(case_dir, "VTK", "*.vtk"),
        os.path.join(case_dir, "VTK", "**", "*.vtu"),
        os.path.join(case_dir, "VTK", "**", "*.vtk"),
    ]

    vtk_files = []
    for pattern in vtk_patterns:
        vtk_files.extend(glob.glob(pattern, recursive=True))

    if not vtk_files:
        print(f"ERROR: No VTK files found in{case_dir}/VTK/")
        print("Make sure you ran: foamToVTK -case " + case_dir)
        return None

    # Use the first VTK file found
    vtk_path = vtk_files[0]
    print(f"Loading:{vtk_path}")

    # Read the VTK file with PyVista
    mesh = pv.read(vtk_path)

    print(f"\n=== Mesh Statistics ===")
    print(f"  Type:{type(mesh).__name__}")
    print(f"  Number of points (vertices):{mesh.n_points}")
    print(f"  Number of cells:{mesh.n_cells}")
    print(f"  Bounds (x_min, x_max, y_min, y_max, z_min, z_max):")
    print(f"{[round(b, 4) for b in mesh.bounds]}")

    # For a 1x1x1 cube with 10x10x10 cells:
    # - Points should be 11x11x11 = 1331
    # - Cells should be 10x10x10 = 1000
    expected_points = 11 * 11 * 11  # 1331
    expected_cells = 10 * 10 * 10   # 1000

    print(f"\n  Expected points:{expected_points}, got:{mesh.n_points}")
    print(f"  Expected cells:{expected_cells}, got:{mesh.n_cells}")

    if mesh.n_points == expected_points and mesh.n_cells == expected_cells:
        print("\nSUCCESS: Mesh matches expected geometry!")
    else:
        print("\nWARNING: Mesh dimensions don't match expected values.")
        print("This may be OK if you changed the cell counts.")

    return mesh

if __name__ == "__main__":
    mesh = load_foam_vtk("~/foam_cases/cube_test")
