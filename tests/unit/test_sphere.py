import classy_blocks as cb
import os
import subprocess

mesh = cb.Mesh()
center = [0, 0, 0]
radius_point = [1, 0, 0]
split = [0, 0, 1]
neg_split = [0, 0, -1]

upper = cb.Hemisphere(center, radius_point, split)
lower = cb.Hemisphere(center, radius_point, neg_split)

for block in (upper, lower):
    block.chop_axial(count=5)
    block.chop_radial(count=5)
    block.chop_tangential(count=5)
    mesh.add(block)

os.makedirs('test_sphere/system', exist_ok=True)
mesh.write('test_sphere/system/blockMeshDict')

with open('test_sphere/system/controlDict', 'w') as f:
    f.write('FoamFile\n{\n    version     2.0;\n    format      ascii;\n    class       dictionary;\n    object      controlDict;\n}\napplication     foamRun;\nstartFrom       startTime;\nstartTime       0;\nstopAt          endTime;\nendTime         1;\ndeltaT          1;\nwriteControl    timeStep;\nwriteInterval   1;\n')

print("Running blockMesh...")
subprocess.run(['blockMesh', '-case', 'test_sphere'])
print("Running foamToVTK...")
res = subprocess.run(['foamToVTK', '-case', 'test_sphere'])
print(f"foamToVTK exited with {res.returncode}")
