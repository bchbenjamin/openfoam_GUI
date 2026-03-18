# DEV_NOTES.md — Classy Blocks Integration

> **Last updated:** 2026-03-18  
> **Status:** Week 2 implementation complete

---

## Project Structure

```
classy_blender_mesh/
├── addon/                        # Blender addon package
│   ├── __init__.py               # [LIVE] Addon registration (imports bpy)
│   ├── case_setup.py             # [LIVE] Generates OF13 case files (controlDict, fvSchemes, etc.)
│   ├── foam_runner.py            # [LIVE] Runs blockMesh/foamToVTK via subprocess with env injection
│   ├── geometry_extractor.py     # [LIVE] Extracts geometry from Blender objects → spec dict
│   ├── mesh_builder.py           # [LIVE] Builds blockMeshDict via classy_blocks API
│   ├── operators.py              # [LIVE] All 4 operators wired to real logic (Weeks 1–2)
│   ├── properties.py             # [LIVE] Object & scene custom properties (basic set)
│   ├── ui.py                     # [LIVE] Panel UI for 3D Viewport sidebar
│   └── vtk_importer.py           # [STUB] Placeholder — reads VTK and creates Blender meshes
├── foam_cases/                   # Example pipeline scripts
│   ├── cube_test/                # OpenFOAM case directory for cube example
│   ├── generate_cube.py          # [LIVE] Generates a cube blockMeshDict
│   └── test_load_vtk.py          # [LIVE] Tests VTK loading with PyVista
├── tests/                        # Automated test suite
│   ├── test_classy.py            # [LIVE] ✅ classy_blocks API test (mesh.add)
│   ├── test_geometry_extractor_unit.py  # [LIVE] ✅ 10 unit tests for geometry extraction
│   ├── test_subprocess_foam.py   # [LIVE] ✅ OpenFOAM subprocess env injection test
│   ├── test_pyvista.py           # [LIVE] ✅ PyVista install and VTK roundtrip test
│   ├── test_lshaped_duct.py      # [LIVE] ✅ Multi-block topology test (2 adjacent boxes)
│   └── test_case_setup.py        # [LIVE] ✅ OF13 case file generation test
├── Progress.md/                  # Planning and tracking documents
│   ├── Classy Blocks Prototype Documentation.md
│   ├── Detailed To Do.md
│   └── toDo.md
├── .gitignore
└── DEV_NOTES.md                  # ← This file
```

---

## Module Status

### Fully Implemented (LIVE)
| Module | Purpose | Standalone testable? |
|---|---|---|
| `mesh_builder.py` | Builds blockMeshDict from spec dict via `classy_blocks` | ✅ Yes |
| `foam_runner.py` | Runs blockMesh/foamToVTK with OF env injection | ✅ Yes |
| `case_setup.py` | Generates OF13 case files (controlDict, fvSchemes, etc.) | ✅ Yes |
| `operators.py` | 4 Blender operators with full error handling | ❌ Blender only |
| `properties.py` | Block & scene properties | ❌ Blender only |
| `ui.py` | 3D Viewport sidebar panel | ❌ Blender only |

### Fully Implemented (NEW — Week 2)
| Module | Purpose | Standalone testable? |
|---|---|---|
| `geometry_extractor.py` | Extracts box/extrude/revolve blocks from Blender → spec dict | ✅ Unit tests (mocked bpy) |

### Placeholder / Stub (STUB)
| Module | Purpose | What's missing |
|---|---|---|
| `vtk_importer.py` | Reads VTK files → creates Blender mesh objects | `load_vtk_as_blender_mesh()` returns `None`, `_parse_pyvista_faces()` and `_remove_existing_object()` are `pass`. `find_vtk_files()` is implemented. |

---

## Operator Wiring (Week 1)

All 4 operators in `operators.py` are now wired with real logic:

| Operator | What it does | Status |
|---|---|---|
| `CLASSY_OT_generate_mesh` | Calls `geometry_extractor.extract_geometry()` → `mesh_builder.build_from_spec()` | ✅ Wired (depends on geometry_extractor stub) |
| `CLASSY_OT_run_blockmesh` | Calls `foam_runner.run_blockmesh()` → parses quality metrics | ✅ Wired |
| `CLASSY_OT_convert_vtk` | Calls `foam_runner.run_foam_to_vtk()` → counts output files | ✅ Wired |
| `CLASSY_OT_reload_mesh` | Calls `vtk_importer.find_vtk_files()` → `load_vtk_as_blender_mesh()` | ✅ Wired (depends on vtk_importer stub) |

All operators include:
- Path validation guard (bail early if `case_path` is empty)
- `try/except` with descriptive error messages via `self.report()`
- Actionable error strings (not just "Failed")

---

## Test Results (2026-03-18)

All automated tests run with `python3 -m pytest tests/ -v` — **14 passed**:

| Test | Result | Notes |
|---|---|---|
| `test_classy.py::test_simple_box` | ✅ PASSED | classy_blocks 1.10.0, `mesh.add()` API |
| `test_geometry_extractor_unit.py` (10 tests) | ✅ ALL PASSED | Bounding box, coord preservation, dispatch, defaults |
| `test_lshaped_duct.py::test_lshaped_duct` | ✅ PASSED | 2-block merge, importlib fix applied |
| `test_pyvista.py::test_pyvista_basic` | ✅ PASSED | PyVista 0.47.1, `.n_cells` fix applied |
| `test_subprocess_foam.py::test_blockmesh_subprocess` | ✅ PASSED | OF13 env injection works |
| `test_case_setup.py` | ✅ PASSED | Runs via `python3 tests/test_case_setup.py` (uses `main()`) |

### Key tests for coordinate preservation
- `test_get_world_bounding_box_translated` — cube at (10,10,10) returns (9,9,9)→(11,11,11) ✅
- `test_extract_box_coordinate_preservation` — same, verifying spec dict output ✅
- `test_extract_geometry_multiple_boxes` — two boxes at different positions, both correct ✅

### Known Warnings (non-blocking)
- `nptyping` deprecation warnings for `np.bool8`, `np.object0`, etc. — cosmetic
- `PytestReturnNotNoneWarning` in `test_subprocess_foam.py`

---

## Dependencies (Confirmed Working)

| Package | Version | Install method |
|---|---|---|
| `classy_blocks` | 1.10.0 | `pip3 install classy-blocks` |
| `pyvista` | 0.47.1 | `pip3 install pyvista` |
| `numpy` | 1.26.4 | `pip3 install numpy` |
| `OpenFOAM` | 13 | `/opt/openfoam13/etc/bashrc` |
| `Python` | 3.12.3 | System |
| `pytest` | 9.0.2 | `pip3 install pytest` |

### Blender Python (Test 5 — to verify manually)
Run in Blender's Scripting workspace:
```python
import classy_blocks; print("classy_blocks OK")
import pyvista; print(f"pyvista {pyvista.__version__}")
import numpy; print(f"numpy {numpy.__version__}")
```

---

## Import Architecture Note

`addon/__init__.py` imports `bpy` which is only available inside Blender. Tests that need `addon` submodules (`mesh_builder`, `case_setup`) use `importlib.util` to load the `.py` file directly, bypassing `__init__.py`. This is the standard pattern for testing Blender addon modules outside of Blender.

---

## Next Steps

1. ~~**Implement `geometry_extractor.py`**~~ ✅ Done (Week 2)
2. **Implement `vtk_importer.py`** (Week 3) — `load_vtk_as_blender_mesh()` still returns `None`
3. **Add grading properties to `properties.py`** (Week 5)
4. **Add autosave properties and handler** (Weeks 5–6, 11)
5. **End-to-end Blender integration test** — Requires steps 1 and 2 above
