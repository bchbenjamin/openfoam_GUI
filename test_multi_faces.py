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
geometry
{
    x16.stl
    {
        type triSurfaceMesh;
        file "x16.stl";
    }
};
vertices
(
        (-1.00000000 -1.00000000 -1.00000000) // 0
        (1.00000000 -1.00000000 -1.00000000) // 1
        (1.00000000 1.00000000 -1.00000000) // 2
        (-1.00000000 1.00000000 -1.00000000) // 3
        (-1.00000000 -1.00000000 1.00000000) // 4
        (1.00000000 -1.00000000 1.00000000) // 5
        (1.00000000 1.00000000 1.00000000) // 6
        (-1.00000000 1.00000000 1.00000000) // 7
);
blocks
(
        hex ( 0 1 2 3 4 5 6 7 ) Cube ( 10 10 10 ) simpleGrading ( 1.0 1.0 1.0 )
);
edges
(
);
boundary
(
);
faces
(
    project (0 1 2 3) x16.stl
    project (4 5 6 7) x16.stl
);
""")

rc = subprocess.run(["bash", "-c", "source /home/bchbenjamin/OpenFOAM/OpenFOAM-13/etc/bashrc && blockMesh -case " + case_path], capture_output=True, text=True)
print("RC:", rc.returncode)
print(rc.stdout)
print(rc.stderr)
