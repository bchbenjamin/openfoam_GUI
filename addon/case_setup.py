"""
OpenFOAM Case Setup utilities.

Handles the generation of required OpenFOAM case files (e.g., controlDict) to ensure
the generated blockMeshDict resides in a valid, runnable environment.
"""

# addon/case_setup.py
# Sets up OpenFOAM 13 case files. Uses the new foamRun + solvers{ } syntax.
# icoFoam/simpleFoam no longer exist as standalone commands in OF13.
#
# This file has NO Blender imports — fully testable with plain Python.
#
# HOW TO USE:
#   from addon.case_setup import setup_incompressible_case
#   setup_incompressible_case(
#       case_path="~/foam_cases/cube_test",
#       patch_names=["inlet", "outlet", "wall"],
#   )
#
# WHAT IT CREATES:
#   system/controlDict   — solver settings (foamRun + incompressibleFluid)
#   system/fvSchemes     — discretisation schemes
#   system/fvSolution    — linear solver settings
#   0/U                  — initial velocity field + boundary conditions
#   0/p                  — initial pressure field + boundary conditions

import os
from typing import List

# -------------------------------------------------------
# OpenFOAM 13 controlDict template.
#
# KEY CHANGE vs OF11:
#   Old: application icoFoam;
#   New: application foamRun;
#        solvers { fluid { solver incompressibleFluid; } }
#
# The double braces {{ }} are Python f-string escapes for literal { }.
# -------------------------------------------------------
CONTROL_DICT_TEMPLATE = """\
FoamFile
{{
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}}

// OpenFOAM 13: foamRun replaces icoFoam, simpleFoam, etc.
// The solver module is now specified inside a 'solvers' sub-dict.
// For transient incompressible flow, the module is 'incompressibleFluid'.
application     foamRun;

solvers
{{
    fluid
{{
        solver{solver_module};
}}
}}

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end_time};
deltaT          {delta_t};
writeControl    timeStep;
writeInterval   {write_interval};
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
timeFormat      general;
timePrecision   6;
runTimeModifiable yes;
"""

# -------------------------------------------------------
# Minimal fvSchemes for transient incompressible flow.
# These scheme choices work for both laminar and low-Re turbulent flows.
# -------------------------------------------------------
FV_SCHEMES_TEMPLATE = """\
FoamFile
{{
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSchemes;
}}

ddtSchemes{{ default Euler;}}
gradSchemes{{ default Gauss linear;}}
divSchemes{{ default none; div(phi,U) Gauss linearUpwind grad(U);}}
laplacianSchemes{{ default Gauss linear corrected;}}
interpolationSchemes{{ default linear;}}
snGradSchemes{{ default corrected;}}
"""

# -------------------------------------------------------
# Minimal fvSolution: PCG for pressure, smoothSolver for velocity.
# These are robust defaults from the icoFoam tutorial cases.
# -------------------------------------------------------
FV_SOLUTION_TEMPLATE = """\
FoamFile
{{
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSolution;
}}

solvers
{{
    p
{{
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0.05;
}}
    U
{{
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0;
}}
}}

PISO
{{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
}}
"""

def setup_incompressible_case(
    case_path: str,
    patch_names: List[str],
    transient: bool = True,
    end_time: float = 0.5,
    delta_t: float = 0.005,
    write_interval: int = 20,
    inlet_velocity: List[float] = [1.0, 0.0, 0.0],
) -> None:
    """
    Sets up an OpenFOAM 13 incompressible flow case.

    For OpenFOAM 13:
    - Transient (previously icoFoam)    → solver module: 'incompressibleFluid'
    - Steady-state (previously simpleFoam) → solver module: 'incompressibleFluid'
      with a 'steady' ddtScheme in fvSchemes

    Args:
        case_path:      Path to the OpenFOAM case directory.
        patch_names:    List of boundary patch names from your mesh
                        (e.g. ["inlet", "outlet", "wall"]).
        transient:      True = time-marching (formerly icoFoam),
                        False = steady-state (formerly simpleFoam).
        end_time:       Simulation end time in seconds.
        delta_t:        Time step size in seconds.
        write_interval: Write results every N time steps.
        inlet_velocity: Inlet velocity vector [Ux, Uy, Uz] in m/s.
    """
    case_path = os.path.expanduser(case_path)
    system_dir = os.path.join(case_path, "system")
    zero_dir = os.path.join(case_path, "0")
    os.makedirs(system_dir, exist_ok=True)
    os.makedirs(zero_dir, exist_ok=True)

    # In OF13, both transient and steady cases use 'incompressibleFluid'.
    # Steady-state is controlled via fvSchemes ddtSchemes (not shown here).
    solver_module = "incompressibleFluid"

    _write(os.path.join(system_dir, "controlDict"),
           CONTROL_DICT_TEMPLATE.format(
               solver_module=solver_module,
               end_time=end_time,
               delta_t=delta_t,
               write_interval=write_interval,
           ))

    _write(os.path.join(system_dir, "fvSchemes"), FV_SCHEMES_TEMPLATE)
    _write(os.path.join(system_dir, "fvSolution"), FV_SOLUTION_TEMPLATE)
    _write(os.path.join(zero_dir, "U"), _build_U(patch_names, inlet_velocity))
    _write(os.path.join(zero_dir, "p"), _build_p(patch_names))

    pass
    pass
    pass

def _write(path: str, content: str) -> None:
    """Writes content to a file, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    pass

def _build_U(patch_names: List[str], inlet_velocity: List[float]) -> str:
    """
    Builds the 0/U boundary condition file.
    Heuristic patch classification by name:
      - 'inlet*'    → fixedValue (velocity inlet)
      - 'outlet*'   → zeroGradient (fully-developed outflow)
      - 'symmetry*' → symmetryPlane
      - anything else → noSlip wall
    """
    ux, uy, uz = inlet_velocity
    bcs = ""
    for p in patch_names:
        if "inlet" in p.lower():
            bcs += f"{p}\n{{\n        type fixedValue;\n        value uniform ({ux}{uy}{uz});\n}}\n"
        elif "outlet" in p.lower():
            bcs += f"{p}\n{{\n        type zeroGradient;\n}}\n"
        elif "symmetry" in p.lower():
            bcs += f"{p}\n{{\n        type symmetryPlane;\n}}\n"
        else:
            bcs += f"{p}\n{{\n        type noSlip;\n}}\n"

    return (
        'FoamFile\n{\n    format ascii;\n    class volVectorField;\n'
        '    location "0";\n    object U;\n}\n\n'
        'dimensions [0 1 -1 0 0 0 0];\n'
        'internalField uniform (0 0 0);\n\n'
        f'boundaryField\n{{\n{bcs}}}\n'
    )

def _build_p(patch_names: List[str]) -> str:
    """
    Builds the 0/p boundary condition file.
    Heuristic classification:
      - 'outlet*' → fixedValue 0 (pressure outlet)
      - anything else → zeroGradient
    """
    bcs = ""
    for p in patch_names:
        if "outlet" in p.lower():
            bcs += f"{p}\n{{\n        type fixedValue;\n        value uniform 0;\n}}\n"
        else:
            bcs += f"{p}\n{{\n        type zeroGradient;\n}}\n"

    return (
        'FoamFile\n{\n    format ascii;\n    class volScalarField;\n'
        '    location "0";\n    object p;\n}\n\n'
        'dimensions [0 2 -2 0 0 0 0];\n'
        'internalField uniform 0;\n\n'
        f'boundaryField\n{{\n{bcs}}}\n'
    )
