import subprocess
import os

case_path = "/home/bchbenjamin/OpenFOAM/OpenFOAM-13/cavity"
bmd = os.path.join(case_path, "system", "blockMeshDict")
os.makedirs(os.path.join(case_path, "constant", "geometry"), exist_ok=True)
with open(os.path.join(case_path, "constant", "geometry", "x16.stl"), "w") as f:
    f.write("solid obj\n  facet normal 0 0 1\n    outer loop\n      vertex 0 0 0\n      vertex 1 0 0\n      vertex 0 1 0\n    endloop\n  endfacet\nendsolid obj\n")

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
faces
(
    project (4 5 6 7) x16.stl
);
boundary
();
mergePatchPairs
();
""")

rc3 = subprocess.run(["bash", "-c", "source /home/bchbenjamin/OpenFOAM/OpenFOAM-13/etc/bashrc && blockMesh -case " + case_path], capture_output=True, text=True)
print("\nFACES FORMAT WITHOUT QUOTES (FILE PRESENT):")
print("RC:", rc3.returncode)
print(rc3.stdout)
print(rc3.stderr)

