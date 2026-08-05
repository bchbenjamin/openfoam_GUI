import subprocess
import os

case_path = "/home/bchbenjamin/OpenFOAM/OpenFOAM-13/cavity"
bmd = os.path.join(case_path, "system", "blockMeshDict")

env = os.environ.copy()

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
(
    {
        name "x16.stl";
        type triSurfaceMesh;
        file "x16.stl";
    }
);
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
();
boundary
();
mergePatchPairs
();
""")

rc = subprocess.run(["bash", "-c", "source /home/bchbenjamin/OpenFOAM/OpenFOAM-13/etc/bashrc && blockMesh -case " + case_path], capture_output=True, text=True)
print("LIST FORMAT:")
print("RC:", rc.returncode)
print(rc.stdout)
print(rc.stderr)

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
        ();
        boundary
        ();
        mergePatchPairs
        ();
        """)

rc2 = subprocess.run(["bash", "-c", "source /home/bchbenjamin/OpenFOAM/OpenFOAM-13/etc/bashrc && blockMesh -case " + case_path], capture_output=True, text=True)
print("\nDICT FORMAT:")
print("RC:", rc2.returncode)
print(rc2.stdout)
print(rc2.stderr)

