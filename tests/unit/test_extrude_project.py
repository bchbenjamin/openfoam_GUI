import classy_blocks as cb
mesh = cb.Mesh()
face = cb.Face([[0,0,0], [1,0,0], [1,1,0], [0,1,0]])
extrude = cb.Extrude(face, [0,0,1])
extrude.chop(0, count=10)
extrude.chop(1, count=10)
extrude.chop(2, count=10)
extrude.project_side("top", "x16.stl")
mesh.add(extrude)
mesh.add_geometry({ "x16.stl": ["type triSurfaceMesh", 'file "x16.stl"'] })
mesh.write("/tmp/test_extrude_bmd")
with open("/tmp/test_extrude_bmd", "r") as f:
    print(f.read())
