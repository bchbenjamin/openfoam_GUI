import sys
from unittest.mock import MagicMock
class MockOperator: pass
mock_bpy = MagicMock()
mock_bpy.types.Operator = MockOperator
sys.modules["bpy"] = mock_bpy

import addon.operators as _op
print("EXTRUDE:", type(_op.CLASSY_OT_extrude_sketch), hasattr(_op.CLASSY_OT_extrude_sketch, "execute"))
