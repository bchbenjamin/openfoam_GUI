# Classy Blocks — Comprehensive To-Do List

> All placeholder code locations and planned additions identified from the
> [Classy Blocks Prototype Documentation.md](file:///home/bchbenjamin/classy_blender_mesh/Classy%20Blocks%20Prototype%20Documentation.md).

---

## 1. Placeholder / Stub Operator Implementations

All 4 operators in `addon/operators.py` have stub `execute()` methods that only print status messages without performing real work.

### 1.1 `CLASSY_OT_generate_mesh.execute()` — Line 7-10
- **File:** `addon/operators.py`
- **Current:** Reports `"Generated: system/blockMeshDict"` without doing anything.
- **Needed:**
  - [ ] Call `geometry_extractor.extract_geometry(context)` to build the spec dict
  - [ ] Get `case_path` from `context.scene.classy_mesh_props.case_path`
  - [ ] Compute `output_path = os.path.join(case_path, "system", "blockMeshDict")`
  - [ ] Call `mesh_builder.build_from_spec(spec, output_path)`
  - [ ] Handle errors and report status to the user

### 1.2 `CLASSY_OT_run_blockmesh.execute()` — Line 15-18
- **File:** `addon/operators.py`
- **Current:** Reports `"blockMesh completed successfully"` without running anything.
- **Needed:**
  - [ ] Get `case_path` and `bashrc_path` from `context.scene.classy_mesh_props`
  - [ ] Call `foam_runner.run_blockmesh(case_path, bashrc_path)`
  - [ ] Parse return code, report stdout/stderr
  - [ ] Call `foam_runner.parse_mesh_quality()` and display non-orthogonality/skewness

### 1.3 `CLASSY_OT_convert_vtk.execute()` — Line 23-25
- **File:** `addon/operators.py`
- **Current:** Reports `"VTK conversion complete"` without running anything.
- **Needed:**
  - [ ] Get `case_path` and `bashrc_path` from scene props
  - [ ] Call `foam_runner.run_foam_to_vtk(case_path, bashrc_path)`
  - [ ] Check return code and report errors

### 1.4 `CLASSY_OT_reload_mesh.execute()` — Line 30-32
- **File:** `addon/operators.py`
- **Current:** Reports `"Mesh reloaded"` without doing anything.
- **Needed:**
  - [ ] Get `case_path` from scene props
  - [ ] Call `vtk_importer.find_vtk_files(case_path)`
  - [ ] Call `vtk_importer.load_vtk_as_blender_mesh(vtk_path)` with the first file found
  - [ ] Handle errors (no VTK files, import failure)

---

## 2. Placeholder `geometry_extractor.py` Functions

**File:** `addon/geometry_extractor.py` *(newly created)*

### 2.1 `extract_geometry(context)`
- [ ] Iterate over `context.scene.objects`
- [ ] Filter for objects with `obj.classy_block_props.is_block == True`
- [ ] Dispatch by `block_type`: "box" → bounding box, "extrude" → face + vector, "revolve" → face + angle + axis
- [ ] Read `cells`, `patch_name`, and `grading` from custom properties
- [ ] Return assembled spec dict

### 2.2 `_get_world_bounding_box(obj)`
- [ ] Use `obj.bound_box` (8 corners) + `obj.matrix_world` to get world-space min/max
- [ ] Return `(p_min, p_max)` lists

### 2.3 `_extract_face_vertices(obj, face_index)`
- [ ] Get evaluated mesh via `depsgraph`
- [ ] Extract 4 world-space vertices from a quad face
- [ ] Return `[[x,y,z], ...]` list

---

## 3. Placeholder `vtk_importer.py` Functions

**File:** `addon/vtk_importer.py` *(newly created)*

### 3.1 `load_vtk_as_blender_mesh(vtk_path, mesh_name)`
- [ ] Load VTK with PyVista: `pv.read(vtk_path)`
- [ ] Extract surface geometry (vertices + faces)
- [ ] Create Blender mesh via `bpy.data.meshes.new()` + `from_pydata()`
- [ ] Create Blender object and link to collection
- [ ] Remove any existing object with the same name first

### 3.2 `_parse_pyvista_faces(pv_faces)`
- [ ] Convert PyVista flat face array `[n, v0, v1, ..., n, v0, v1, ...]` to Blender tuple format `[(v0,v1,v2,v3), ...]`

### 3.3 `_remove_existing_object(name)`
- [ ] Remove existing Blender object + orphan mesh data before re-import

---

## 4. Missing Properties (Phase 8 — Advanced Features)

**File:** `addon/properties.py`

### 4.1 Grading properties on `ClassyMeshObjectProperties`
- [ ] Add `grading_type: EnumProperty` — choices: RATIO, START_SIZE, SYMMETRIC
- [ ] Add `grading: FloatVectorProperty` — per-axis c2c expansion ratios (default `(1.0, 1.0, 1.0)`)
- [ ] Add `start_size: FloatProperty` — first cell size in meters for wall refinement
- [ ] Add `end_size: FloatProperty` — last cell size for symmetric grading

### 4.2 STL Projection properties
- [ ] Add `stl_projection_face: EnumProperty` — which face to project (top, bottom, front, back, left, right)
- [ ] Add `stl_file: StringProperty` — path to target STL file

---

## 5. Missing Operator (Phase 8 — Advanced Features)

**File:** `addon/operators.py`

### 5.1 `MESH_OT_export_terrain_stl`
- [ ] Create new operator class with `bl_idname = "mesh.classy_export_terrain"`
- [ ] Export selected Blender object as STL to `<case>/constant/triSurface/terrain.stl`
- [ ] Use `bpy.ops.wm.stl_export(filepath=stl_path, use_selection=True)`
- [ ] Register in `addon/__init__.py`

---

## 6. Missing `mesh_builder.py` Extension (Phase 8)

**File:** `addon/mesh_builder.py`

### 6.1 `build_box_block_with_stl(mesh, spec)`
- [ ] Add function that builds a Box block and optionally projects faces onto an STL
- [ ] Handle `spec["stl_projections"]` dict mapping face names → STL filenames
- [ ] Call `box.project_face(face_name, stl_name)` for each projection

### 6.2 Update `build_from_spec()` to support STL projections
- [ ] Detect `stl_projections` key in block specs
- [ ] Route to `build_box_block_with_stl()` instead of `build_box_block()` when present

### 6.3 Advanced grading support
- [ ] Support `start_size` / `end_size` parameters in `chop()` calls
- [ ] Update block builder functions to read grading_type from spec and dispatch accordingly

---

## 7. UI Panel Additions

**File:** `addon/ui.py`

### 7.1 Grading controls in the Block Properties section
- [ ] Show `grading_type` dropdown when `is_block` is True
- [ ] Conditionally show `start_size` / `end_size` fields based on grading type

### 7.2 STL Export button
- [ ] Add "Export as Terrain STL" button in the panel
- [ ] Only show when an object is selected

### 7.3 Status display
- [ ] Show mesh quality metrics (non-orthogonality, skewness) after blockMesh runs
- [ ] Consider adding a status label that updates after each pipeline step

---

## 8. `__init__.py` Registration Gaps

**File:** `addon/__init__.py`

- [ ] Register `MESH_OT_export_terrain_stl` when it's implemented
- [ ] Add grading properties to `ClassyMeshObjectProperties` registration
- [ ] Consider adding `geometry_extractor` and `vtk_importer` to module imports *(done)*

---

## 9. Testing Gaps

### 9.1 Existing tests that need no changes (verified matching docs)
- [x] `tests/test_classy.py` — Test 2: classy_blocks installation
- [x] `tests/test_subprocess_foam.py` — Test 4: OpenFOAM subprocess
- [x] `tests/test_lshaped_duct.py` — Phase 8.3: multi-block topology
- [x] `tests/test_case_setup.py` — Phase 9: CfdOF case setup
- [x] `tests/test_pyvista.py` — Test 3: PyVista installation *(newly created)*

### 9.2 Existing pipeline scripts (verified matching docs)
- [x] `foam_cases/generate_cube.py` — Phase 1 Step 1.2: cube mesh generation
- [x] `foam_cases/test_load_vtk.py` — Phase 1 Step 1.5: VTK loading verification

### 9.3 Not automated / Blender-only tests
- [ ] Test 1: `blockMesh --version` / `foamToVTK --version` — terminal command, not a script
- [ ] Test 5: Blender Python environment check — must be run inside Blender's Scripting workspace

### 9.4 Future tests to add
- [ ] Unit test for `geometry_extractor.extract_geometry()` (requires Blender or mocking bpy)
- [ ] Unit test for `vtk_importer.load_vtk_as_blender_mesh()` (requires Blender or mocking bpy)
- [ ] Integration test: full pipeline from spec dict → blockMeshDict → blockMesh → VTK → mesh stats
- [ ] Test for `MESH_OT_export_terrain_stl` operator
- [ ] Test for grading options (start_size, end_size, c2c_expansion)

---

## 10. Case Template Files (Phase 9)

These are generated programmatically by `case_setup.py`, not stored as static files:

- [x] `system/controlDict` — uses `foamRun` + `incompressibleFluid` (OF13 format)
- [x] `system/fvSchemes` — discretisation schemes
- [x] `system/fvSolution` — linear solver settings
- [x] `0/U` — velocity boundary conditions (auto-classified by patch name)
- [x] `0/p` — pressure boundary conditions

---

## Summary

| Category | Total Items | Done | Remaining |
|---|---|---|---|
| Operator implementations | 4 | 0 | **4** |
| geometry_extractor functions | 3 | 0 | **3** |
| vtk_importer functions | 3 | 0 | **3** |
| Properties additions | 4+ | 0 | **4+** |
| New operators | 1 | 0 | **1** |
| mesh_builder extensions | 3 | 0 | **3** |
| UI panel additions | 3 | 0 | **3** |
| __init__ registration | 2 | 1 | **1** |
| Tests (verified) | 7 | 7 | 0 |
| Future tests | 5 | 0 | **5** |
