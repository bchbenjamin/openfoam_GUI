# test_subprocess_foam.py
# Tests that blockMesh can be called from Python subprocess with OpenFOAM 13.
# Run with: python3 test_subprocess_foam.py

import subprocess
import os
import sys

def find_openfoam_env():
    """
    Sources the OpenFOAM bashrc and captures the resulting environment.
    Checks OpenFOAM 13 first, then falls back to older versions.
    """
    candidates = [
        "/opt/openfoam13/etc/bashrc",   # OpenFOAM Foundation v13 (current)
        "/opt/openfoam12/etc/bashrc",
        "/opt/openfoam11/etc/bashrc",
        "/usr/lib/openfoam/openfoam2406/etc/bashrc",  # ESI/OpenCFD variant
    ]

    for bashrc_path in candidates:
        if os.path.exists(bashrc_path):
            print(f"Found OpenFOAM bashrc:{bashrc_path}")
            result = subprocess.run(
                ["bash", "-c", f'source "{bashrc_path}" && env'],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"  WARNING: Could not source it:{result.stderr[:200]}")
                continue

            env = {}
            for line in result.stdout.splitlines():
                if "=" in line:
                    key, _, value = line.partition("=")
                    env[key] = value
            return env, bashrc_path

    return None, None

def test_blockmesh_subprocess():
    env, bashrc_path = find_openfoam_env()

    if env is None:
        print("ERROR: No OpenFOAM installation found.")
        print("Install OpenFOAM 13: https://openfoam.org/download/13-ubuntu/")
        sys.exit(1)

    result = subprocess.run(
        ["blockMesh", "--version"],
        capture_output=True, text=True, env=env
    )

    # blockMesh --version may return exit code 1 on some OF versions — that is normal
    version_output = (result.stdout + result.stderr).strip()
    if not version_output:
        print("ERROR: blockMesh produced no output. Is it actually installed?")
        print(f"  PATH in env:{env.get('PATH', 'NOT SET')}")
        sys.exit(1)

    print(f"SUCCESS: blockMesh callable from Python subprocess!")
    print(f"  Output:{version_output}")
    print(f"  Sourced from:{bashrc_path}")
    return env

if __name__ == "__main__":
    test_blockmesh_subprocess()
