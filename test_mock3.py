import sys
from unittest.mock import MagicMock
import numpy as np
np.bool8 = np.bool_

class MockOperator: pass
mock_bpy = MagicMock()
mock_bpy.types.Operator = MockOperator
mock_bpy.props.EnumProperty = MagicMock(return_value=None)
mock_bpy.props.FloatProperty = MagicMock(return_value=None)
mock_bpy.props.IntProperty = MagicMock(return_value=None)
sys.modules["bpy"] = mock_bpy
sys.modules["bmesh"] = MagicMock()
sys.modules["gpu"] = MagicMock()
sys.modules["gpu_extras"] = MagicMock()
sys.modules["gpu_extras.batch"] = MagicMock()
sys.modules["mathutils"] = MagicMock()
sys.modules["mathutils.geometry"] = MagicMock()
sys.modules["bpy_extras"] = MagicMock()

import addon.operators as _op
print("Type:", type(_op.CLASSY_OT_extrude_sketch))
print("Has execute:", hasattr(_op.CLASSY_OT_extrude_sketch, "execute"))
if hasattr(_op.CLASSY_OT_extrude_sketch, "execute"):
    print("execute:", type(_op.CLASSY_OT_extrude_sketch.execute))
