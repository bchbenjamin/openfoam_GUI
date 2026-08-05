import os
import sys
from unittest.mock import MagicMock
sys.modules['bpy'] = MagicMock()
sys.modules['gpu'] = MagicMock()
sys.modules['gpu_extras'] = MagicMock()
sys.modules['gpu_extras.batch'] = MagicMock()
sys.modules['bmesh'] = MagicMock()
sys.modules['mathutils'] = MagicMock()
sys.modules['mathutils.geometry'] = MagicMock()
sys.modules['bpy_extras'] = MagicMock()

import subprocess
import pytest
from addon import foam_runner, case_setup

def test_degenerate_blockmesh(tmp_path):
    """

    Args:
      tmp_path: 

    Returns:

    """
    case_path = str(tmp_path)
    os.makedirs(os.path.join(case_path, "system"), exist_ok=True)
    
    # We write a blockMeshDict manually to avoid classy_blocks import error in test env
    # (since the test env might have the numpy error too, wait, if test_subprocess_foam.py works, maybe not?)
    
    dict_content = """
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       dictionary;
        object      blockMeshDict;
    }
    
    scale   1;
    
    vertices
    (
        (0 0 0)
        (0 1 0)
        (1 1 0)
        (1 0 0)
        (0 0 1)
        (0 1 1)
        (1 1 1)
        (1 0 1)
    );
    
    blocks
    (
        // CW bottom face creates an inside-out hex if top face corresponds
        hex (0 1 2 3 4 5 6 7) (10 10 10) simpleGrading (1 1 1)
    );
    
    edges
    (
    );
    
    boundary
    (
    );
    
    mergePatchPairs
    (
    );
    """
    
    with open(os.path.join(case_path, "system", "blockMeshDict"), "w") as f:
        f.write(dict_content)
        
    case_setup.setup_incompressible_case(case_path, [])
    
    print("Running blockMesh on inside-out hex...")
    ret, out, err = foam_runner.run_blockmesh(case_path, "")
    print("Exit code:", ret)
    print("Stdout:", out[-500:])
    print("Stderr:", err[-500:])
    
    assert ret != 0
    assert "inside-out" in err or "inside-out" in out
