# test_classy.py
# Tests that classy_blocks can create a simple cube mesh dict.
# Run with: python3 test_classy.py
# Expected result: creates "blockMeshDict_test" in the current directory

import os

os.environ.setdefault("NUMBA_DISABLE_JIT", "1")

import classy_blocks as cb

def test_simple_box():
    mesh = cb.Mesh()

    box = cb.Box([0, 0, 0], [1, 1, 1])
    box.chop(0, count=10)
    box.chop(1, count=10)
    box.chop(2, count=10)

    # CORRECT API: mesh.add(), NOT mesh.merge()
    mesh.add(box)

    output_path = "blockMeshDict_test"
    mesh.write(output_path)#, tolerance=1e-4)

    assert os.path.exists(output_path), "ERROR: blockMeshDict_test was not created!"
    size = os.path.getsize(output_path)
    assert size > 100, f"ERROR: File too small ({size} bytes)"

    print(f"SUCCESS: blockMeshDict_test created ({size} bytes)")
    print("First 10 lines:")
    with open(output_path) as f:
        for i, line in enumerate(f):
            if i >= 10: break
            print(f"{line}", end="")

if __name__ == "__main__":
    test_simple_box()
