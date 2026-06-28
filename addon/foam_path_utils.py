"""
OpenFOAM Path Utilities.

Provides helper functions to resolve, validate, and manage directory paths for
OpenFOAM cases to ensure safety and correctness before execution.
"""

# addon/foam_path_utils.py
# Pure-Python utilities for OpenFOAM path validation and normalization.
# No Blender imports — fully testable with plain Python/pytest.
#
# PURPOSE:
#   Bridge the gap between the environment configuration (foam_directories.py)
#   and the pipeline operators (operators.py). Provides a single source of truth
#   for path resolution, containment checking, and write-permission verification.
#
# DESIGN DECISIONS:
#   - All paths are resolved via os.path.realpath() to flatten symlinks.
#     Linux workstations frequently symlink /opt/openfoam* or home directories
#     across partitions. Without resolution, string-based containment checks
#     produce false negatives.
#   - Write permission is checked pre-emptively using os.access(path, os.W_OK).
#     If the target directory doesn't exist yet, we walk up to the nearest
#     existing ancestor and check write access there.
#   - "Warn-but-allow" philosophy: validation returns warnings, never raises.

import os
from typing import Dict, List


def resolve_case_path(case_path: str) -> str:
    """
    Normalizes an OpenFOAM case path to a canonical absolute form.

    Applies in order:
      1. Strip leading/trailing whitespace
      2. Expand ~ to the user's home directory
      3. Strip trailing slashes (prevents double-slash issues in os.path.join)
      4. Resolve symlinks to their physical targets (os.path.realpath)
      5. Convert to absolute path

    Args:
        case_path: Raw path string from user input or Blender property.

    Returns:
        Cleaned, absolute, symlink-resolved path string.
        Returns empty string if input is empty/whitespace-only.
    """
    if not case_path or not case_path.strip():
        return ""
    path = case_path.strip()
    path = os.path.expanduser(path)
    path = path.rstrip('/')
    path = os.path.realpath(path)
    return os.path.abspath(path)


def validate_case_path(case_path: str, foam_run_dir: str = "") -> Dict:
    """
    Validates a case path against the OpenFOAM environment context.

    Checks performed:
      1. Path is non-empty after normalization.
      2. Directory exists (or its parent is writable for new cases).
      3. Write permission is verified on the target or nearest ancestor.
      4. If foam_run_dir is set, checks whether case_path is a subdirectory.

    All checks produce warnings, never raise exceptions. The caller decides
    whether to block or allow execution based on the returned flags.

    Args:
        case_path:    Raw case directory path (will be resolved internally).
        foam_run_dir: The configured $FOAM_RUN path (may be empty if not set).

    Returns:
        Dict with keys:
          - valid (bool): True if the path is usable for file operations.
          - is_inside_foam_run (bool): True if case_path is under foam_run_dir.
          - writable (bool): True if the target or ancestor is writable.
          - warnings (list[str]): Human-readable warning strings.
          - resolved_path (str): The normalized, symlink-resolved path.
    """
    result = {
        "valid": False,
        "is_inside_foam_run": False,
        "writable": False,
        "warnings": [],
        "resolved_path": "",
    }

    resolved = resolve_case_path(case_path)
    result["resolved_path"] = resolved

    # Check 1: Non-empty
    if not resolved:
        result["warnings"].append("Case path is empty.")
        return result

    # Check 2: Exists as a directory (or parent is writable for creation)
    if os.path.exists(resolved):
        if not os.path.isdir(resolved):
            result["warnings"].append(
                f"Case path points to a file, not a directory: {resolved}"
            )
            return result
    # If it doesn't exist, that's okay — we'll check parent writability below

    # Check 3: Write permission
    result["writable"] = _check_write_access(resolved)
    if not result["writable"]:
        result["warnings"].append(
            f"No write permission for case path (or nearest ancestor): {resolved}"
        )

    # Path is usable if it's non-empty and writable
    result["valid"] = bool(resolved) and result["writable"]

    # Check 4: FOAM_RUN containment
    if foam_run_dir and foam_run_dir.strip():
        resolved_run = resolve_case_path(foam_run_dir)
        if resolved_run:
            result["is_inside_foam_run"] = _is_subdirectory(resolved, resolved_run)
            if not result["is_inside_foam_run"]:
                result["warnings"].append(
                    f"Case path is outside $FOAM_RUN ({resolved_run}). "
                    "The pipeline will still run, but this case may not be "
                    "visible to standard OpenFOAM workflows."
                )
    else:
        # No FOAM_RUN configured — skip containment check, no warning
        result["is_inside_foam_run"] = True

    return result


def is_valid_openfoam_case(path: str) -> bool:
    """
    Checks if a directory looks like a valid OpenFOAM case.

    A valid case has a system/ subdirectory (the minimum required structure
    for blockMesh to find controlDict and blockMeshDict).

    Args:
        path: Absolute path to check.

    Returns:
        True if the directory exists and contains a system/ subdirectory.
    """
    resolved = resolve_case_path(path)
    if not resolved:
        return False
    system_dir = os.path.join(resolved, "system")
    return os.path.isdir(system_dir)


def _is_subdirectory(child: str, parent: str) -> bool:
    """
    Check if child is a subdirectory of (or equal to) parent.

    Both paths must already be resolved via os.path.realpath() to handle
    symlinks correctly. Uses os.path.commonpath() for robust comparison
    instead of string prefix matching.

    Args:
        child:  Resolved absolute path of the candidate child.
        parent: Resolved absolute path of the candidate parent.

    Returns:
        True if child is inside parent (or is parent itself).
    """
    try:
        # commonpath returns the longest common sub-path
        common = os.path.commonpath([child, parent])
        return common == parent
    except ValueError:
        # On Windows, commonpath raises ValueError for paths on different drives
        return False


def _check_write_access(path: str) -> bool:
    """
    Verify write access for a path, walking up to the nearest existing ancestor.

    If the target directory exists, checks os.access(path, os.W_OK) directly.
    If it doesn't exist yet, walks up the directory tree to find the nearest
    existing parent and checks write access there (since os.makedirs would
    need to create the missing segments).

    Args:
        path: Absolute path to check.

    Returns:
        True if the user has write access to the target or its nearest ancestor.
    """
    check_path = path
    while check_path and check_path != os.path.dirname(check_path):
        if os.path.exists(check_path):
            return os.access(check_path, os.W_OK)
        check_path = os.path.dirname(check_path)
    # Reached filesystem root
    if os.path.exists(check_path):
        return os.access(check_path, os.W_OK)
    return False
