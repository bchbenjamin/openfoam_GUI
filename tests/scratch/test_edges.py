import subprocess
import os

case_path = "/tmp/test_repro_case"
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
geometry
{
    "x16.stl"
    {
        type triSurfaceMesh;
        file "x16.stl";
    }
}
vertices
(
    (0 0 0) (1 0 0) (1 1 0) (0 1 0)
    (0 0 1) (1 0 1) (1 1 1) (0 1 1)
);
blocks
(
    hex (0 1 2 3 4 5 6 7) (1 1 1) simpleGrading (1 1 1)
);
edges
(
    project 0 1 x16.stl
);
boundary
();
""")

rc3 = subprocess.run(["bash", "-c", "source /home/bchbenjamin/OpenFOAM/OpenFOAM-13/etc/bashrc && blockMesh -case " + case_path], capture_output=True, text=True)
print("\nEDGES FORMAT:")
print("RC:", rc3.returncode)
print(rc3.stdout)
print(rc3.stderr)

