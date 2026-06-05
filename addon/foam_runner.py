# addon/foam_runner.py
# Runs OpenFOAM 13 utilities as subprocesses with correct environment injection.
# No Blender imports — fully testable with plain Python.
#
# WHY ENVIRONMENT INJECTION IS NEEDED:
#   OpenFOAM utilities like blockMesh are only available AFTER sourcing:
#     source /opt/openfoam13/etc/bashrc
#   Python subprocesses don't inherit shell-sourced environments. So we source
#   the bashrc in a bash subprocess, capture its env vars, and pass them to
#   subsequent subprocess calls — simulating what the terminal does.

import os
import re
import subprocess
from typing import Tuple, Optional, Dict

# -------------------------------------------------------
# Default fallback bashrc path if addon preferences are not available
# (e.g. when running outside Blender, or in tests).
# In normal operation, operators always pass the user-configured
# preferences.bashrc_path value from AddonPreferences.
# -------------------------------------------------------
def get_default_bashrc() -> str:
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    for name in ["OpenFOAM-13", "openfoam13"]:
        local_bashrc = os.path.join(addon_dir, name, "etc", "bashrc")
        if os.path.exists(local_bashrc):
            return local_bashrc
    return "/opt/openfoam13/etc/bashrc"

DEFAULT_BASHRC = get_default_bashrc()


def get_bashrc_path(bashrc_path: str = "") -> str:
    """
    Resolves the OpenFOAM bashrc path.

    Priority:
      1. Explicitly passed bashrc_path (from operator calling code)
      2. DEFAULT_BASHRC module-level fallback

    Args:
        bashrc_path: Path passed by the caller (usually from AddonPreferences).

    Returns:
        The resolved bashrc path string.
    """
    if bashrc_path and bashrc_path.strip():
        return os.path.expanduser(bashrc_path.strip())
    return DEFAULT_BASHRC

def get_openfoam_environment(bashrc_path: str) -> Dict[str, str]:
    """
    Sources the OpenFOAM bashrc and returns the resulting environment as a dict.

    This is required because Python subprocesses don't inherit shell-sourced envs.
    We achieve this by running: bash -c 'source <bashrc> && env'
    and parsing the output line-by-line into a dict.
    """
    if not os.path.exists(bashrc_path):
        raise FileNotFoundError(
            f"OpenFOAM bashrc not found:{bashrc_path}\n"
            "For OpenFOAM 13 on Ubuntu, the path should be:\n"
            "  /opt/openfoam13/etc/bashrc\n"
            "Install from: https://openfoam.org/download/13-ubuntu/"
        )

    result = subprocess.run(
        ["bash", "-c", f'source "{bashrc_path}" && env'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to source OpenFOAM environment:\n{result.stderr[:500]}"
        )

    # Parse 'env' output: each line is KEY=value
    env = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            env[key] = value
    return env

def run_blockmesh(case_path: str, openfoam_bashrc: str = "") -> Tuple[int, str, str]:
    """
    Runs: blockMesh -case <case_path>
    Works identically in OpenFOAM 13 (blockMesh command is unchanged).

    Returns: (return_code, stdout, stderr)
    A return_code of 0 means success.
    """
    resolved_bashrc = get_bashrc_path(openfoam_bashrc)
    env = get_openfoam_environment(resolved_bashrc)
    case_path = os.path.expanduser(case_path)

    # Validate the case directory and blockMeshDict exist before running
    if not os.path.isdir(case_path):
        raise FileNotFoundError(f"Case directory not found:{case_path}")

    bmd = os.path.join(case_path, "system", "blockMeshDict")
    if not os.path.exists(bmd):
        raise FileNotFoundError(
            f"blockMeshDict not found:{bmd}\n"
            "Run 'Generate blockMeshDict' first."
        )

    result = subprocess.run(
        ["blockMesh", "-case", case_path],
        capture_output=True, text=True, env=env
    )
    return result.returncode, result.stdout, result.stderr

def run_foam_to_vtk(case_path: str, openfoam_bashrc: str = "") -> Tuple[int, str, str]:
    """
    Runs: foamToVTK -case <case_path>

NOTE for OpenFOAM 13: foamToVTK still works and is the method used here
    for the Blender re-import workflow. Alternatively, you can create an empty
    'case.foam' file in the case directory and open it directly in ParaView
    without needing foamToVTK at all:
        touch ~/foam_cases/cube_test/cube_test.foam

    Returns: (return_code, stdout, stderr)
    """
    resolved_bashrc = get_bashrc_path(openfoam_bashrc)
    env = get_openfoam_environment(resolved_bashrc)
    case_path = os.path.expanduser(case_path)

    poly_mesh = os.path.join(case_path, "constant", "polyMesh")
    if not os.path.isdir(poly_mesh):
        raise FileNotFoundError(
            f"polyMesh not found:{poly_mesh}\n"
            "Run blockMesh first."
        )

    result = subprocess.run(
        ["foamToVTK", "-case", case_path],
        capture_output=True, text=True, env=env
    )
    return result.returncode, result.stdout, result.stderr

def parse_mesh_quality(blockmesh_output: str) -> Dict[str, Optional[float]]:
    """
    Parses blockMesh stdout/stderr for mesh quality metrics.

    blockMesh reports these at the end of a successful run:
      Max non-orthogonality = XX.X
      Max skewness = X.X

    Good mesh: non-orthogonality < 70, skewness < 4.
    """
    quality = {"non_orthogonality": None, "skewness": None}

    m = re.search(r"Max non-orthogonality\s*=\s*([\d.]+)", blockmesh_output)
    if m:
        quality["non_orthogonality"] = float(m.group(1))

    m = re.search(r"Max skewness\s*=\s*([\d.]+)", blockmesh_output)
    if m:
        quality["skewness"] = float(m.group(1))

    return quality
