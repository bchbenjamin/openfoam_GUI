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
    "x16.stl"
    {
        type triSurfaceMesh;
        file "x16.stl";
    }
}
vertices
(
    project (0 0 0) x16.stl
);
blocks
(
);
edges
();
boundary
();
""")

rc3 = subprocess.run(["bash", "-c", "source /home/bchbenjamin/OpenFOAM/OpenFOAM-13/etc/bashrc && blockMesh -case " + case_path], capture_output=True, text=True)
print("\nVERTICES FORMAT:")
print("RC:", rc3.returncode)
print(rc3.stdout)
print(rc3.stderr)

