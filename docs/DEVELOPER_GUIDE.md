# Developer Guide
This guide is for contributors extending the Classy Blender Mesh add-on. It assumes you are already familiar with Python and Blender's add-on API. For historical context and week-by-week decisions, see [DEV_NOTES.md](../DEV_NOTES.md).
---
## Architecture Overview
The add-on follows a **spec-dict pipeline** — every block type passes through the same three stages:
```
Blender Scene Objects
        │
        ▼
geometry_extractor.py   ←─ reads bpy objects, produces spec dicts
        │
        │  {"type": "box", "p_min": [...], "p_max": [...], "cells": [...], ...}
        │
        ▼
mesh_builder.py         ←─ consumes spec dicts, calls classy_blocks API
        │
        │  cb.Box / cb.Cylinder / cb.Extrude / ...
        │
        ▼
blockMeshDict (file)    ←─ mesh.write(output_path)
        │
        ▼
foam_runner.py          ←─ subprocess: blockMesh, foamToVTK
        │
        ▼
vtk_importer.py         ←─ PyVista loads VTK, creates Blender mesh object
```
The `operators.py` module wires these stages together into Blender operator `execute()` methods. The `ui.py` panel renders the buttons and per-block property fields. The two layers never call each other — they only talk through the operator.
---
## Module Reference
### `addon/__init__.py`
Registers all classes and properties. `bl_info` targets Blender 4.0+. Includes `@bpy.app.handlers.persistent` post-load handler that restores the last case directory and hooks `sketch_tool.unregister_handlers()` into global `unregister()`.
### `addon/operators.py`
All Blender operators. Every operator follows the same pattern (see **Conventions** below).
| Operator | `bl_idname` | Description |
|---|---|---|
| `CLASSY_OT_generate_mesh` | `classy.generate_mesh` | Runs extractor → builder → case setup |
| `CLASSY_OT_run_blockmesh` | `classy.run_blockmesh` | Shells out to `blockMesh`, parses quality metrics |
| `CLASSY_OT_convert_vtk` | `classy.convert_vtk` | Shells out to `foamToVTK` |
| `CLASSY_OT_reload_mesh` | `classy.reload_mesh` | Loads VTK result into Blender via PyVista |
| `CLASSY_OT_run_all` | `classy.run_all` | Runs all four steps sequentially |
| `CLASSY_OT_project_to_stl` | `classy.project_to_stl` | Validates an STL file via `stl_projector.validate_stl()` |
| `MESH_OT_export_terrain_stl` | `mesh.classy_export_terrain` | Exports selected mesh as terrain STL into the case |
| `CLASSY_OT_add_box` | `classy.add_box` | Adds a cube pre-tagged as BOX |
| `CLASSY_OT_add_cylinder` | `classy.add_cylinder` | Adds a cylinder pre-tagged as CYLINDER |
| `CLASSY_OT_add_frustum` | `classy.add_frustum` | Adds a cone pre-tagged as FRUSTUM |
| `CLASSY_OT_extrude_sketch` | `classy.extrude_sketch` | Tags a curve sketch for EXTRUDE + validates 4 points |
| `CLASSY_OT_revolve_sketch` | `classy.revolve_sketch` | Tags a curve sketch for REVOLVE + validates 4 points |
| `CLASSY_OT_tag_extrude` | `classy.tag_extrude` | Edit-mode: tags a selected quad face as EXTRUDE |
| `CLASSY_OT_tag_revolve` | `classy.tag_revolve` | Edit-mode: tags a selected quad face as REVOLVE |
| `CLASSY_OT_tag_loft` | `classy.tag_loft` | Edit-mode: tags two selected quad faces as LOFT |
| `CLASSY_OT_add_boundary_patch` | `classy.add_boundary_patch` | Adds an entry to `face_patches` list |
| `CLASSY_OT_remove_boundary_patch` | `classy.remove_boundary_patch` | Removes the selected `face_patches` entry |
### `addon/geometry_extractor.py`
Reads every object in `context.scene.objects` and produces the spec dict. Dispatches by `obj.classy_block_props.block_type`. Handles:
- Curve objects tagged `classy_sketch=True` (fast-path to `_build_sketch_spec` / `_build_extrude_spec` / `_build_revolve_spec`).
- `_extract_face_vertices_local_bmesh()` for EXTRUDE/REVOLVE/LOFT face extraction (uses `bmesh` to read vertex coords reliably in edit and object mode).
- `_read_grading()`, `_read_cells()`, `_read_chain_params()` helpers for reading `classy_block_props`.
- Injects `stl_projections` dict into specs for supported block types when `props.stl_file` is set.
- Returns `{"blocks": [...], "merge_tolerance": 1e-4, "warnings": [...]}`.
**Note:** `_compute_mesh_volume` does not exist in the current codebase — the `test_geometry_extractor_unit.py` test harness patches it, which causes 12 test failures (see **Known Test Failures**).
### `addon/mesh_builder.py`
Purely Python; no `import bpy`. Receives the spec dict from the extractor and calls the `classy_blocks` API. Completely stand-alone testable.
The `_BUILDERS` dict maps type strings to build functions:
```python
_BUILDERS = {
    "box": _build_box, "cylinder": _build_cylinder, "frustum": _build_frustum,
    "sphere": _build_sphere, "disk": _build_disk, "extrude": _build_extrude,
    "revolve": _build_revolve, "loft": _build_loft, "wedge": _build_wedge,
    "extruded_ring": _build_extruded_ring, "unsupported": _build_unsupported,
}
```
`build_from_spec()` does a **two-pass** build to handle shape chaining:
- **Pass 1:** Non-chained blocks; Cylinder/Frustum builders return their `cb` object (stored in `built_shapes[name]`).
- **Pass 2:** Chained blocks; calls `_build_chained_block(mesh, spec, source_shape)`.
**Fail-loudly policy:** `build_block()` raises `ValueError` for unknown block types. Individual build functions let `classy_blocks` exceptions propagate. There is **no global try/except** wrapping per-block building — if a block fails, the pipeline aborts with a traceback. This is deliberate.
### `addon/sketch_tool.py`
The `CLASSY_OT_add_sketch_point` modal operator. Key design points:
- Uses **`gpu` + `gpu_extras.batch`** for the draw handler (compatible with Blender 4.0+; `bgl` is removed in Blender 4.0).
- The WINDOW region and `region_3d` are captured in `invoke()` from the panel button context to get correct screen-to-world ray coordinates (the panel region and the viewport region are different objects — mixing them causes incorrect raycasts).
- `_cleanup()` fires on all three exit paths: `FINISHED`, `CANCELLED`, and unhandled exception (the `except` block in `modal()`).
- `_active_draw_handlers` is a module-level list; `unregister_handlers()` cleans it up when the add-on is disabled mid-sketch.
- The created curve object is tagged `obj["classy_sketch"] = True` for the extractor.
### `addon/stl_projector.py`
No `import bpy` — fully stand-alone testable. Two distinct purposes:
1. **`validate_stl(filepath)`** — used by the UI Validate button. Checks manifold status and triangle count.
2. **`project_face_to_stl(spec, face_name, stl_path)`** — Python-side pre-warp fallback. **Not used in the primary pipeline**, which uses `classy_blocks`'s native `project_side()` + `mesh.add_geometry()` instead. The native route is strictly better (see `mesh_builder._apply_stl_projections` docstring).
### `addon/properties.py`
Defines `ClassyMeshObjectProperties` (per-object), `ClassyMeshSceneProperties` (per-scene), and `ClassyFacePatch` (collection item). Source of truth for all panel-exposed properties.
### `addon/foam_runner.py`, `addon/case_setup.py`
Subprocess wrappers. `foam_runner.run_blockmesh()` sources the OpenFOAM `bashrc` and runs `blockMesh`. `foam_runner.parse_mesh_quality()` extracts non-orthogonality and skewness from the combined stdout/stderr. `case_setup.setup_incompressible_case()` writes `controlDict`, `fvSchemes`, `fvSolution`, and `0/` initial conditions.
### `addon/vtk_importer.py`
Uses PyVista to load a `.vtk` file, converts it to a Blender mesh object. `find_vtk_files()` searches the `VTK/` subdirectory.
---
## Conventions
### Operator Pattern
Every operator must follow this exact structure:
```python
class CLASSY_OT_my_operator(bpy.types.Operator):
    bl_idname = "classy.my_operator"
    bl_label = "My Operator"
    def execute(self, context):
        case_path = get_case_path(context)
        # 1. Path guard — bail early with a popup + self.report
        if not case_path:
            context.window_manager.popup_menu(draw_error, ...)
            self.report({'ERROR'}, "Case directory is not set")
            return {'CANCELLED'}
        # 2. Validated action inside try/except
        try:
            do_something()
            self.report({'INFO'}, "Success message")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Actionable error: {str(e)}")
            return {'CANCELLED'}
```
**Never** silently swallow errors with `pass` after a `self.report({'ERROR'}, ...)`. The user must always see why the pipeline stopped.
### `importlib.util` Testing Pattern
`addon/__init__.py` imports `bpy` at module level. Pytest cannot import it without a live Blender process. The solution: mock all Blender modules into `sys.modules` **before** importing any addon submodule.
```python
import sys
from unittest.mock import MagicMock
class MockOperator:
    pass
mock_bpy = MagicMock()
mock_bpy.types.Operator = MockOperator  # must be a real class, not a Mock
sys.modules["bpy"] = mock_bpy
sys.modules["bmesh"] = MagicMock()
sys.modules["gpu"] = MagicMock()
sys.modules["gpu_extras"] = MagicMock()
sys.modules["gpu_extras.batch"] = MagicMock()
sys.modules["mathutils"] = MagicMock()
sys.modules["bpy_extras"] = MagicMock()
# Now safe to import addon submodules
import addon.operators as _op
import addon.mesh_builder as _mb
```
`bpy.types.Operator` must be a real Python class (not a `MagicMock`) so that operator class definitions using it as a base class actually work. If it's a `MagicMock`, the `spec=str` constraint causes `AttributeError` when the class body is executed.
---
## How to Add a New Block Type
1. **`properties.py`**: Add the type string to the `block_type` `EnumProperty` items list. Add any new parameters as `FloatProperty` / `IntProperty` / `StringProperty` on `ClassyMeshObjectProperties`.
2. **`geometry_extractor.py`**: Add an `elif block_type == "MY_TYPE":` branch in `extract_geometry()` that calls a new `_build_my_type_spec(obj, props)` function. The spec dict must always include:
   - `"type"`: lowercase string matching the builder key
   - `"name"`: `obj.name`
   - `"cells"`: from `_read_cells(props)`
   - `"patch_name"`: from `_read_patch_name(props)`
   - `**_read_grading(props)`
   - `**_read_chain_params(props)`
   - `"matrix_world"`: `[list(row) for row in obj.matrix_world]`
3. **`mesh_builder.py`**: Write `_build_my_type(mesh, spec)` and add it to `_BUILDERS`. Follow the existing pattern: create a `cb.*` object, call `_apply_chops()` or `_apply_round_chops()`, optionally call `_apply_stl_projections()`, call `_apply_face_patches()`, then `mesh.add(shape)`.
4. **`ui.py`**: Add an `elif props.block_type == "MY_TYPE":` branch in the per-object panel to expose the new properties.
5. **`operators.py`**: If you add a new tagged primitive button, add an operator like `CLASSY_OT_add_my_type` and register it in `__init__.py`.
6. **Tests**: Add a unit test in a new or existing test file. Use the `importlib.util` mocking pattern. Test at minimum: valid input produces the correct spec keys, and `mesh_builder._build_my_type()` runs without error against a real `cb.Mesh`.
---
## Testing
### Run the Suite
```bash
python3 -m pytest tests/ -v --ignore=tests/test_blender_integration.py
```
### Test Files
| File | What it tests |
|---|---|
| `test_classy.py` | Raw `classy_blocks` API sanity check |
| `test_mesh_builder_stl.py` | STL projection via `_apply_stl_projections()` |
| `test_stl_projector.py` | `load_stl()`, `validate_stl()`, `project_face_to_stl()` |
| `test_geometry_extractor_unit.py` | Spec extraction for Box, Cylinder, Sphere, Extrude, Revolve |
| `test_extrude_revolve.py` | `CLASSY_OT_extrude_sketch`, `CLASSY_OT_revolve_sketch` operators |
| `test_sketch_tool.py` | Handler registration / cleanup for `CLASSY_OT_add_sketch_point` |
| `test_loft_wedge_builder.py` | `_build_loft()`, `_build_wedge()` end-to-end |
| `test_frustum_builder.py` | `_build_frustum()` |
| `test_chain_builder.py` | Shape chaining (Cylinder.chain, Frustum.chain) |
| `test_grading.py` | Grading modes (RATIO, START_SIZE, SYMMETRIC) |
| `test_cone_detection.py` | Cone/frustum auto-detection heuristics |
| `test_vtk_importer_unit.py` | VTK file loading and face parsing |
| `test_foam_path_utils.py` | Case path resolution and validation |
| `test_tutorial_copy_sets_case_path.py` | Tutorial manager workflow |
| `test_lshaped_duct.py` | Multi-block L-shaped duct (integration test) |
| `test_subprocess_foam.py` | OpenFOAM subprocess environment injection |
| `test_pyvista.py` | PyVista install sanity |
| `test_case_setup.py` | OpenFOAM case file generation |
| `test_blender_integration.py` | *(Skipped in headless CI — requires live Blender)* |
### Known Pre-Existing Failures (Do Not Re-Diagnose)
**All 12 failures are in `test_geometry_extractor_unit.py`** and have two root causes:
1. **`_compute_mesh_volume` mock mismatch** (10 failures): The test harness uses `patch.object(_ge, '_compute_mesh_volume', ...)` to inject a mock volume for auto-detection tests. This function no longer exists at the `geometry_extractor` module level under that name (the implementation moved). The tests fail at collection/setup with `AttributeError: module 'geometry_extractor' does not have the attribute '_compute_mesh_volume'`. This is a **test harness bug**, not a runtime bug — the pipeline works correctly in Blender.
2. **`bmesh.new` mock miss** (2 failures — `test_block_type_dispatch_extrude`, `test_block_type_dispatch_revolve`): The mocked `bmesh` module has `new` as a `MagicMock`, but `bmesh.from_edit_mesh()` / `bmesh.new()` pattern fails silently, causing the spec builder to fall through to `_make_unsupported_spec()` instead of building an extrude/revolve spec. The tests assert `len(result["blocks"]) == 0`, but one block is returned with type `"unsupported"`.
These are known and pre-existing. A new contributor should fix `test_geometry_extractor_unit.py`'s mock setup, not `geometry_extractor.py` itself.
