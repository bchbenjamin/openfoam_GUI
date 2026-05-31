# generate_cube.py
# Generates a blockMeshDict for a simple 1x1x1 cube case.
#
# HOW TO RUN:
#   cd ~/foam_cases
#   python3 generate_cube.py
#
# WHAT IT DOES:
#   Creates system/blockMeshDict inside ~/foam_cases/cube_test/
#   This file will be read by blockMesh in the next step.
#
# EXPECTED OUTPUT:
#   "SUCCESS: Written blockMeshDict to ..."

import os
import classy_blocks as cb

def generate_cube_mesh():
    # The case directory where we want to write the blockMeshDict.
    # This path must already exist (we created it in Step 1.1).
    case_dir = os.path.expanduser("~/foam_cases/cube_test")
    output_path = os.path.join(case_dir, "system", "blockMeshDict")

    # -------------------------------------------------------
    # Create the mesh object. Think of this as a container
    # that holds all your blocks before writing them out.
    # -------------------------------------------------------
    mesh = cb.Mesh()

    # -------------------------------------------------------
    # Create a Box block.
    # cb.Box(p_min, p_max) defines a rectangular box by its
    # two opposite corners.
    #
    # p_min = [x_min, y_min, z_min]  (bottom-left-back corner)
    # p_max = [x_max, y_max, z_max]  (top-right-front corner)
    #
    # Here we make a unit cube: 1m x 1m x 1m
    # -------------------------------------------------------
    box = cb.Box([0, 0, 0], [1, 1, 1])

    # -------------------------------------------------------
    # Set cell counts using .chop()
    # box.chop(direction, count=N) divides the block in the
    # given direction into N equal cells.
    #
    # direction 0 = x-axis
    # direction 1 = y-axis
    # direction 2 = z-axis
    #
    # 10 cells in each direction = 10x10x10 = 1000 cells total
    # -------------------------------------------------------
    box.chop(0, count=10)
    box.chop(1, count=10)
    box.chop(2, count=10)

    # -------------------------------------------------------
    # Add the block to the mesh.
    # mesh.add() is how you add blocks. When you have
    # multiple touching blocks later, it also merges their
    # shared faces automatically.
    # -------------------------------------------------------
    mesh.add(box)

    # -------------------------------------------------------
    # Write the blockMeshDict file.
    # tolerance: vertices closer than this will be merged.
    # 1e-4 (= 0.0001 meters) is a safe default.
    # -------------------------------------------------------
    mesh.write(output_path)#, tolerance=1e-4)

    # Verify the file was written
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"SUCCESS: Written blockMeshDict to{output_path} ({size} bytes)")
    else:
        print(f"ERROR: File was not created at{output_path}")

if __name__ == "__main__":
    generate_cube_mesh()
