# test_pyvista.py
# Tests that PyVista is installed and working.
# Run with: python3 test_pyvista.py
# Expected result: prints mesh info for a generated sphere surface

import pyvista as pv
import numpy as np

def test_pyvista_basic():
    """
    Creates a simple sphere mesh using PyVista's built-in generators,
    then reads its properties. This tests the core reading/writing workflow
    without needing a real VTK file from OpenFOAM.
    """
    # Create a sphere (built-in PyVista function, no file needed)
    sphere = pv.Sphere(radius=1.0, center=(0, 0, 0))

    print(f"SUCCESS: PyVista is working!")
    print(f"  Sphere mesh has {sphere.n_points} vertices and {sphere.n_faces} faces")
    print(f"  Bounds: {sphere.bounds}")

    # Test that we can extract vertices and faces (same operation we will use for real meshes)
    vertices = sphere.points
    print(f"  First vertex: {vertices[0]}")
    print(f"  Vertex array shape: {vertices.shape} (N x 3 array of x,y,z coordinates)")

    # Test saving and re-reading a VTK file
    sphere.save("/tmp/test_sphere.vtk")
    reloaded = pv.read("/tmp/test_sphere.vtk")
    assert reloaded.n_points == sphere.n_points, "ERROR: VTK save/load roundtrip failed!"
    print(f"  VTK save/load roundtrip: OK")

if __name__ == "__main__":
    test_pyvista_basic()
