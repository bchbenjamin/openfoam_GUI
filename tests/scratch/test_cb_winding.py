import os, sys, shutil
from classy_blocks import Mesh, Face, Extrude
import subprocess

def test_extrude(pts, sweep, name) -> None:
    """

    Args:
      pts: 
      sweep: 
      name: 

    Returns:

    """
    mesh = Mesh()
    base = Face(pts)
    op = Extrude(base, sweep)
    op.chop(0, count=10)
    op.chop(1, count=10)
    op.chop(2, count=10)
    mesh.add(op)
    
    case_dir = "/tmp/cb_test_" + name
    if os.path.exists(case_dir):
        shutil.rmtree(case_dir)
    os.makedirs(case_dir + "/system")
    
    mesh.write(case_dir + "/system/blockMeshDict")
        
    code, out = subprocess.getstatusoutput(f"blockMesh -case {case_dir}")
    if code != 0:
        print(f"{name}: FAILED (inside-out)")
    else:
        print(f"{name}: SUCCESS")

pts1 = [[0,0,0], [1,0,0], [1,1,0], [0,1,0]] 

# Sweep is +Z. Normal is +Z. (align)
test_extrude(pts1, [0,0,1], "align_extrude")

# Sweep is -Z. Normal is +Z. (oppose)
test_extrude(pts1, [0,0,-1], "oppose_extrude")

