import os, sys, shutil
from classy_blocks import Mesh, Face, Extrude
import subprocess

def test_extrude(pts, sweep, name):
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
    os.system(f"cp foam_cases/default_case/system/controlDict {case_dir}/system/")
        
    code, out = subprocess.getstatusoutput(f"blockMesh -case {case_dir}")
    if code != 0:
        print(f"{name}: FAILED (inside-out)")
    else:
        print(f"{name}: SUCCESS")

pts1 = [[0,0,0], [1,0,0], [1,1,0], [0,1,0]] 

# pts1 normal is +Z. Sweep is -Z. (oppose)
# My extractor REVERSES the points before passing to classy_blocks!
pts_reversed = list(reversed(pts1)) # Now normal is -Z
# Now we extrude towards -Z.
test_extrude(pts_reversed, [0,0,-1], "reversed_oppose")

