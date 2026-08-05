import classy_blocks as cb
mesh = cb.Mesh()
box = cb.Box([0,0,0], [1,1,1])
box.chop(0, count=10)
box.chop(1, count=10)
box.chop(2, count=10)
box.project_side("top", '"x16.stl"')
mesh.add(box)
mesh.add_geometry({ '"x16.stl"': ["type triSurfaceMesh", 'file "x16.stl"'] })
mesh.write("/tmp/test_bmd4")
with open("/tmp/test_bmd4", "r") as f:
    print(f.read())
