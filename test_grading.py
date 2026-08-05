import subprocess
import os

case_path = "/home/bchbenjamin/OpenFOAM/OpenFOAM-13/cavity"
bmd = os.path.join(case_path, "system", "blockMeshDict")

with open(bmd, "w") as f:
    f.write("""
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
vertices ();
blocks
(
    hex (0 1 2 3 4 5 6 7) x16.stl (10 10 10) simpleGrading x16.stl
);
edges ();
faces ();
boundary ();
""")

rc = subprocess.run(["bash", "-c", "source /home/bchbenjamin/OpenFOAM/OpenFOAM-13/etc/bashrc && blockMesh -case " + case_path], capture_output=True, text=True)
print("RC:", rc.returncode)
print(rc.stdout)
print(rc.stderr)
