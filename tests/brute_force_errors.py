import subprocess
import os

case_path = "/home/bchbenjamin/OpenFOAM/OpenFOAM-13/cavity"
bmd = os.path.join(case_path, "system", "blockMeshDict")

template = """
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
}
vertices
(
    (0 0 0) (1 0 0) (1 1 0) (0 1 0)
    (0 0 1) (1 0 1) (1 1 1) (0 1 1)
);
blocks
(
    hex (0 1 2 3 4 5 6 7) (10 10 10) simpleGrading (1 1 1)
);
edges
(
);
faces
(
);
boundary
(
);
"""

places = {
    "geometry_list": template.replace("geometry\n{", "geometry\nx16.stl\n{", 1),
    "vertices_list": template.replace("vertices\n(", "vertices\nx16.stl\n(", 1),
    "blocks_list": template.replace("blocks\n(", "blocks\nx16.stl\n(", 1),
    "edges_list": template.replace("edges\n(", "edges\nx16.stl\n(", 1),
    "faces_list": template.replace("faces\n(", "faces\nx16.stl\n(", 1),
    "boundary_list": template.replace("boundary\n(", "boundary\nx16.stl\n(", 1),
}

for name, content in places.items():
        """ """
    with open(bmd, "w") as f:
        f.write(content)
    rc = subprocess.run(["bash", "-c", "source /home/bchbenjamin/OpenFOAM/OpenFOAM-13/etc/bashrc && blockMesh -case " + case_path], capture_output=True, text=True)
    if "Expected a '('" in rc.stderr or "Expected a '('" in rc.stdout:
        print(f"FOUND MATCH in {name}!")
        print(rc.stderr if "Expected a '('" in rc.stderr else rc.stdout)
        
