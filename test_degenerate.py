import os
import subprocess
import classy_blocks as cb
from addon import foam_runner, case_setup

def test_inside_out():
    case_path = "/tmp/test_inside_out"
    os.makedirs(os.path.join(case_path, "system"), exist_ok=True)
    
    # Create CW vs CCW face
    # Proper CCW face around Z: (0,0,0), (1,0,0), (1,1,0), (0,1,0)
    # Inside-out CW face: (0,0,0), (0,1,0), (1,1,0), (1,0,0)
    face_pts = [
        [0, 0, 0],
        [0, 1, 0],
        [1, 1, 0],
        [1, 0, 0],
    ]
    extrude_vec = [0, 0, 1]
    
    mesh = cb.Mesh()
    ext = cb.Extrude(cb.Face(face_pts), extrude_vec)
    ext.chop(0, count=10)
    ext.chop(1, count=10)
    ext.chop(2, count=10)
    mesh.add(ext)
    
    dict_path = os.path.join(case_path, "system", "blockMeshDict")
    mesh.format()
    mesh.write(dict_path)
    
    case_setup.setup_incompressible_case(case_path, ["defaultWall"])
    
    print("Running blockMesh on inside-out hex...")
    ret, out, err = foam_runner.run_blockmesh(case_path, "")
    print("Exit code:", ret)
    print("Stdout:", out[-500:])
    print("Stderr:", err[-500:])

if __name__ == "__main__":
    test_inside_out()
