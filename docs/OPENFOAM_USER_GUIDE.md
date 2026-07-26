# OpenFOAM User Guide
This guide is for CFD engineers who already know `blockMeshDict` syntax, grading, patches, and `searchableSurface`. It explains how each feature of this add-on maps to — or deviates from — a hand-written OpenFOAM workflow.
---
## What the Add-on Generates
The add-on produces a single `system/blockMeshDict` via the `classy_blocks` Python library, then calls `blockMesh` as a subprocess. It also generates a minimal case scaffold (`controlDict`, `fvSchemes`, `fvSolution`, `0/` directory) suitable as a starting point for incompressible solvers. **You are expected to edit the generated case files** — the scaffold is not solver-ready without tuning.
---
## Block Types and Their `blockMeshDict` Equivalents
### Box
Maps to a single `hex` block spanning `p_min → p_max` in axis-aligned local space. The object's `matrix_world` is passed to `classy_blocks` via `.transform()`, so rotations and translations work correctly. Scale, however, should be applied (`Ctrl+A`) before export to avoid unexpected results from non-unit scaling.
The generated blockMeshDict section is a standard 8-vertex hex with the cell count and grading you specified.
### Cylinder
Maps to a 12-block O-grid cross-section — the standard structured cylinder topology. **You do not draw a circle in Blender and tag it as a cylinder.** You add a primitive cylinder mesh via the panel button; the extractor reads its axis endpoints and radius from the local bounding box. `classy_blocks`'s `cb.Cylinder` then generates the O-grid automatically.
Key parameters exposed:
- **Radial cells** (`cells[0]`): cells from cylinder axis to wall
- **Tangential cells** (`cells[1]`): cells around the circumference (per O-grid segment)
- **Axial cells** (`cells[2]`): cells along the cylinder axis
> ⚠ **Do not apply rotations** to Cylinder, Frustum, or ExtrudedRing objects with `Ctrl+A → Rotations`. The extractor reads these shapes' geometry in local Z-up space; applying rotations destroys the parametric bounding-box assumptions and will produce an invalid spec.
### Frustum (Truncated Cone)
Maps to `cb.Frustum(axis_pt1, axis_pt2, radius_point_1, radius_2)`. The extractor reads bottom and top cap radii from the evaluated mesh vertices. If `radius_2 < 1e-6` (a true cone point), it is clamped to `max(radius_1 * 0.01, 1e-4)` — `classy_blocks` cannot handle a zero end radius.
### Extruded Ring
Maps to `cb.ExtrudedRing(axis_pt1, axis_pt2, outer_radius_pt, inner_radius)`. Requires a hollow cylinder mesh (modelled as an annulus). The extractor reads inner and outer radii at the bottom face. If they are equal or either is zero, it falls through to `unsupported`.
### Extrude (MESH object)
Select a quad face in Edit Mode → **Tag as Extrude Block**. The tagged face index is stored in `props.extrude_face_index`. The extractor reads the 4 face vertices with `bmesh` and produces:
```python
cb.Extrude(cb.Face([v0, v1, v2, v3]), [dx, dy, dz])
```
Extrusion axis and distance are controlled by `extrude_axis` (X/Y/Z) and `extrude_distance` properties in the panel. The extrusion vector is axis-aligned.
> If you need an oblique extrusion vector, you currently need to extend `_build_extrude_spec()` to accept an arbitrary vector property — only axis-aligned vectors are exposed in the current UI.
### Extrude (CURVE / Sketch object)
When the active object is a `ClassySketch` curve (tagged `classy_sketch=True`), **Extrude Sketch** sets `block_type = 'EXTRUDE'` on the curve's properties. The extractor takes the first spline's control points (must be exactly 4) and feeds them as the `cb.Face`. Extrusion axis and distance are still taken from `props.extrude_axis` and `props.extrude_distance` — the sketch only defines the profile shape.
### Revolve
Maps to `cb.Revolve(cb.Face([v0,v1,v2,v3]), angle_radians, axis_vector, origin_point)`.
Parameters exposed in the panel:
- `revolve_face_index` or sketch points (must be 4)
- `revolve_angle` (degrees — converted to radians internally)
- `revolve_axis` (X/Y/Z unit vector)
- `revolve_origin` (3D point)
This is equivalent to hand-writing a revolve block in `blockMeshDict`. The face is the 2D cross-section; `origin` and `axis` define the sweep axis.
### Loft
Maps to `cb.Loft(bottom_face, top_face)`. Requires two quad faces selected in Edit Mode → **Tag as Loft Block**. The extractor reads both face vertex positions. Both faces must have exactly 4 vertices; the faces do not need to be parallel or the same size.
### Wedge (Axisymmetric)
Maps to `cb.Wedge(face, angle_radians)`. The wedge revolves the face symmetrically around the x-axis by ±`angle/2`. This is the standard OpenFOAM axisymmetric 2D setup where you specify a 5°-wide slice and apply `wedge` boundary conditions at both cut faces.
`classy_blocks`'s Wedge always revolves around the **x-axis**. If your model is oriented differently, rotate your geometry before tagging.
### Sphere
Maps to two `cb.Hemisphere` objects sharing a geometry label. The hemispheres are split along an axis inferred from the object's world rotation (defaulting to `[0,0,1]`). Both hemispheres are added to the mesh; `classy_blocks` handles the block-face merging between them.
---
## STL Terrain Projection
### The Native Mechanism (What the Add-on Uses)
When you set an STL file on a block, the pipeline calls:
```python
mesh.add_geometry({"terrain.stl": ["type triSurfaceMesh", 'file "terrain.stl"']})
shape.project_side("top", "terrain.stl")
```
This emits a `geometry {}` section and `project` directives into `blockMeshDict`. `blockMesh` then resolves the projection at runtime using OpenFOAM's own `triSurfaceMesh` reader — **it projects every mesh point on the face, not just the 4 corner vertices**. This means grading is preserved, curvature is interpolated correctly, and the result is equivalent to what you'd get from a hand-written `project` entry.
The STL must be in `constant/triSurface/` or `constant/geometry/` (both directories are written by the **Export as Terrain STL** button).
### STL Validation
**Validate STL** (the button in the panel) calls `stl_projector.validate_stl()` via PyVista. It checks:
- Whether the STL loads at all (empty / malformed files are rejected).
- `is_manifold` (watertight status). A non-manifold STL will produce a warning — `blockMesh` may still project successfully on a non-manifold surface depending on the query location, but boundary edges can cause missed projections.
- Triangle count: STLs with > 500,000 triangles get a performance warning.
### Faces Available for Projection
| Block type | Valid `stl_projection_face` values |
|---|---|
| Box | `top`, `bottom`, `front`, `back`, `left`, `right` |
| Cylinder | `top`, `bottom`, `outer` |
| Frustum | `top`, `bottom`, `outer` |
| Extrude | `top`, `bottom` |
| Loft | `top`, `bottom` |
Only one face per block is exposed in the current UI (the `stl_projection_face` enum). If you need simultaneous projection on multiple faces, edit `geometry_extractor._inject_stl_projections()` to build a multi-key `stl_projections` dict.
### Python Fallback (`stl_projector.project_face_to_stl`)
The module also contains `project_face_to_stl()`, which pre-warps block corner vertices onto the STL using PyVista ray casting. This is **not used in the primary pipeline** — it's the inferior approach because it moves only the 4 control points and relies on `blockMesh` to linearly interpolate between them, which fails on curved terrain. It exists as a fallback for cases where the native `searchableSurface` mechanism isn't available.
---
## Shape Chaining (Pipe Networks)
Cylinders and Frustums expose a **Chain From** field that links one block to another. When set, the chained block is built with `cb.Cylinder.chain(source, length)` or `cb.Frustum.chain(source, length, radius_2)`. This is equivalent to computing the end-face vertices of the source block manually and writing the next block starting from them — the chain mechanism does this automatically in `classy_blocks`.
Only `CYLINDER` and `FRUSTUM` blocks can be chain sources. The pipeline does a two-pass build (see `mesh_builder.build_from_spec`) to ensure source blocks are built before their dependents.
---
## Boundary Conditions and Patches
The **Boundary Conditions** panel on each block stores a list of `(side_name, patch_name, patch_type)` tuples. These are passed to `classy_blocks`'s `shape.set_patch(patch_name, side_name)` call. The `patch_type` field is stored in the spec dict and written into the case's `constant/polyMesh/boundary` section by `case_setup.py`.
What is **not** exposed:
- `inGroups` — not currently written.
- Per-face grading overrides — grading is per-block, applied uniformly across all axes (or with START_SIZE/SYMMETRIC).
- `mergePatchPairs` — blocks adjacent in world space share vertices automatically via `classy_blocks`'s merge tolerance.
---
## Grading
Three modes are exposed per block:
| Mode | `blockMeshDict` equivalent |
|---|---|
| `RATIO` | `simpleGrading` with a per-axis expansion ratio. `[1,1,1]` = uniform. |
| `START_SIZE` | `simpleGrading` computed from a target first-cell width. |
| `SYMMETRIC` | `simpleGrading` with matching start and end widths (double-sided grading). |
For round shapes (Cylinder, Frustum, ExtrudedRing, Sphere), the three axes map to radial / tangential / axial via the dedicated `chop_radial()`, `chop_tangential()`, `chop_axial()` helpers. `blockMeshDict` does not have a `radial` axis concept natively — `classy_blocks` maps these to the hex-block axes it controls internally.
---
## Mesh Quality Readout
After `blockMesh` runs, the add-on parses `non_orthogonality` and `skewness` from the combined stdout/stderr. These are displayed in the panel as **Last Quality** with a color indicator:
| Metric | Threshold | Indicator |
|---|---|---|
| Non-orthogonality | > 70° → Error, > 60° → Warning | `ERROR` / `QUESTION` icon |
| Skewness | > 4.0 → Error, > 2.0 → Warning | `ERROR` / `QUESTION` icon |
These match OpenFOAM's own recommended limits for stable solvers.
---
## What You Still Need to Hand-Edit
- **Solver settings** (`fvSolution`, `fvSchemes`): the scaffold writes defaults suitable for a simple incompressible steady-state run. Transient, compressible, multiphase, or turbulent cases need manual edits.
- **Initial and boundary condition files** (`0/U`, `0/p`, etc.): the scaffold creates empty `0/` directories. You must add field files.
- **`constant/transportProperties`** or turbulence model constants.
- **Complex `mergePatchPairs`**: the add-on does not expose this — adjacent blocks in the scene merge automatically if their vertices coincide within `merge_tolerance = 1e-4`.
- **Multiple STL face projections on a single block**: currently only one face per block is exposed via the UI.
