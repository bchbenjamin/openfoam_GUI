import os, sys, shutil, math
from classy_blocks import Mesh, Face, Revolve
import subprocess

def test_revolve(pts, name) -> None:
    """

    Args:
      pts: 
      name: 

    Returns:

    """
    mesh = Mesh()
    base = Face(pts)
    op = Revolve(base, math.radians(90.0), [0,0,1], [0,0,0])
    op.chop(0, count=10)
    op.chop(1, count=10)
    op.chop(2, count=10)
    mesh.add(op)
    
    case_dir = "/tmp/cb_test_" + name
    if os.path.exists(case_dir):
        shutil.rmtree(case_dir)
    os.makedirs(case_dir + "/system")
    
    mesh.write(case_dir + "/system/blockMeshDict")
    os.system(f"cp foam_cases/default_case/system/controlDict {case_dir}/system/")
        
    code, out = subprocess.getstatusoutput(f"blockMesh -case {case_dir}")
    if code != 0:
        print(f"{name}: FAILED (inside-out)")
    else:
        print(f"{name}: SUCCESS")

# Face in XY plane, centered at X=2.
# Points CCW:
pts = [[3,0,0], [2,1,0], [1,0,0], [2,-1,0]]
# Normal is +Z. Sweep is +Y.
test_revolve(pts, "perpendicular_revolve")

