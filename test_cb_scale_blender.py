import sys
sys.path.append("/home/bchbenjamin/.local/lib/python3.14/site-packages") # or wherever classy_blocks is for blender

# Let's just run it in Blender
import bpy
import os
import sys

# find classy_blocks
import classy_blocks as cb

cyl = cb.Cylinder([0,0,0], [0,0,1], [1,0,0])
try:
    cyl.scale([1, 2, 3])
    print("SUCCESS_SCALE_LIST")
except Exception as e:
    print("FAILED_SCALE_LIST:", e)

try:
    cyl.scale(2.0)
    print("SUCCESS_SCALE_FLOAT")
except Exception as e:
    print("FAILED_SCALE_FLOAT:", e)
