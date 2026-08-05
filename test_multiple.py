import classy_blocks as cb
mesh = cb.Mesh()
mesh.add_geometry({ "x16.stl": ["type triSurfaceMesh", 'file "x16.stl"'] })
mesh.add_geometry({ "x16.stl": ["type triSurfaceMesh", 'file "x16.stl"'] })
mesh.write("/tmp/test_multiple")
with open("/tmp/test_multiple", "r") as f:
    print(f.read())
