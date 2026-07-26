# Beginner's Guide: Classy Blender Mesh
This guide walks you through every implemented feature, step by step, with checkpoints so you know when each step has worked. It assumes you are new to structured meshing but are comfortable using Blender.
**What this tool does:** It converts the 3D objects you build in Blender into a structured hex mesh for OpenFOAM — so instead of writing a `blockMeshDict` by hand, you model shapes visually and click a button.
---
## Before You Start
### Installation Checklist
1. You have **Blender 4.0 or newer** installed.
2. You have **OpenFOAM 13** installed, and `blockMesh` is available in your terminal.
3. You have installed the add-on:
   - In Blender: **Edit → Preferences → Add-ons → Install** → select the `addon/` folder.
   - Enable **"Classy Blocks Integration"** from the add-on list.
4. Open the **N-panel** in the 3D Viewport (press **N**) and select the **ClasyMesh** tab.
**✓ Checkpoint:** If the tab shows a panel with a "Case Settings" field, the add-on is loaded. If it shows "Missing Python Packages" with an Install button, click it and wait for it to finish.
---
## Part 1: Setting the Case Directory
Every feature that runs OpenFOAM needs to know where to write files.
1. In the sidebar, find **Case Settings**.
2. Click the folder icon next to **Case Path** and navigate to an existing directory (or create one, e.g., `~/openfoam_cases/test_case`).
**✓ Checkpoint:** The field shows the path you chose. If the "Run All" button at the bottom gives a "Case directory is not set" popup when clicked, the path is empty or not set.
---
## Part 2: Adding Primitives
The simplest way to add a block is to use the **Add Classy Primitives** panel at the top of the sidebar (it only appears in Object Mode).
### Add a Box
1. Click **Box** in the primitives row.
2. A cube appears in the viewport, already tagged as a **BOX** block.
3. Move, scale, and rotate it to position your domain.
**✓ Checkpoint:** With the cube selected, the sidebar shows "Block Type: BOX" in the per-object section.
> **Why apply scale?** If you scale an object in Blender and don't apply the scale (`Ctrl+A → Scale`), the object's local dimensions don't match what Blender reports. The add-on warns you with a yellow "⚠ Unapplied Scale" message. For boxes, it's okay — the add-on uses the world bounding box. For cylinders and frustums, always apply scale first.
### Add a Cylinder
1. Click **Cylinder** in the primitives row.
2. A cylinder mesh appears, tagged as **CYLINDER**.
3. The sidebar shows Cell counts for Radial, Tangential, and Axial directions.
**✓ Checkpoint:** "Block Type: CYLINDER" appears in the sidebar. The Shape Chaining section also appears below.
> **Why can't I draw a circle and tag it as cylinder?** OpenFOAM's structured cylinder mesh is a specific 12-block "O-grid" topology, not a single cylindrical block. The add-on generates this automatically from the primitive — if you tried to use an arbitrary circle mesh, the topology would be wrong.
### Add a Frustum (Tapered Cylinder)
1. Click **Frustum** in the primitives row.
2. A tapered cone (with a flat top) appears. You can adjust the radii in Blender's operator panel (F9) after adding.
**✓ Checkpoint:** "Block Type: FRUSTUM" in the sidebar.
---
## Part 3: Configuring a Block
With any mesh object selected, the sidebar shows the per-object configuration. Here is what each section does.
### Cell Count
The **Cells** field (`cells[0], cells[1], cells[2]`) controls how many hexahedral cells are placed in each direction. For a box, these are X/Y/Z. For a cylinder, they are radial/tangential/axial.
### Patch Name
This is the default OpenFOAM boundary name for all faces of this block (e.g., `walls`, `inlet`, `outlet`). You can override specific faces in the **Boundary Conditions** section below.
### Block Type
The **Block Type** dropdown lets you manually override how the block is interpreted. The options are BOX, CYLINDER, FRUSTUM, EXTRUDED_RING, WEDGE, EXTRUDE, REVOLVE, LOFT. The primitives panel sets this automatically.
### Grading
**Grading** controls how cells are distributed — uniform or concentrated near a wall.
- **RATIO**: Enter a number > 1 to pack cells toward one end (e.g., `4.0` puts 4× more cells at the far end). Use `1.0` for uniform spacing.
- **START_SIZE**: Enter the absolute width of the first cell in metres (useful for boundary layer control).
- **SYMMETRIC**: Enter both a start and end size; cells are graded from both ends toward the middle.
### Boundary Conditions
The **Boundary Conditions** section lets you assign named OpenFOAM patches to specific faces.
1. Click **+** to add a patch entry.
2. Set the **Side Name** (e.g., `top`, `bottom`, `left`, `right` for a box).
3. Set the **Patch Name** (e.g., `inlet`).
4. Set the **Patch Type** (e.g., `wall`, `patch`, `symmetry`).
**✓ Checkpoint:** After adding a patch, the list shows one row with the three fields. When you run Generate, this face will have its own `inlet { type patch; }` entry in `constant/polyMesh/boundary`.
---
## Part 4: STL Terrain Projection
This lets you conform one face of a block to follow a surface imported from an STL file — useful for terrain meshing.
### Step 1: Prepare the Terrain
If your terrain mesh is already in Blender as a mesh object:
1. Select it.
2. In the sidebar, scroll down to **Terrain Utilities**.
3. Click **Export as Terrain STL**.
**✓ Checkpoint:** An info message says "Terrain STL exported to .../constant/triSurface/terrain.stl". Two copies are written — one in `triSurface/` and one in `geometry/`.
If you already have a terrain STL file, skip to Step 2 and browse directly to it.
### Step 2: Assign the STL to a Block
1. Select the block you want to conform to terrain (e.g., a Box for a channel domain).
2. In the **STL Face Projection** section:
   - **Projection Face**: choose which face to project (e.g., `top` or `bottom`).
   - **STL File**: browse to the terrain STL.
### Step 3: Validate the STL
1. Click **Validate STL**.
**✓ Checkpoint:** An info message appears saying "STL Valid (N triangles, manifold=True)".
- If you see "not manifold (watertight)", the STL has open edges. The mesh may still project, but results near the boundary gaps can be wrong.
- If you see "Failed: file not found", double-check the path.
### Step 4: Generate
Click **Generate blockMeshDict** (or **Run All**). The `blockMeshDict` will contain a `geometry {}` section and `project` entry on the selected face.
**✓ Checkpoint:** Open `system/blockMeshDict` in a text editor. Near the end you should see a `geometry { terrain.stl { ... } }` section.
---
## Part 5: Tagging Edit-Mode Faces (Extrude / Revolve / Loft)
For shapes where you want full control over which face becomes the starting profile, use Edit Mode tagging.
### Extrude from a Quad Face
1. Select a mesh object.
2. Enter Edit Mode (`Tab`).
3. Select the face you want to extrude (it **must** be a quad — 4 vertices).
4. In the sidebar, under **2D Sketch Tools**, click **Tag as Extrude Block**.
**✓ Checkpoint:** "Tagged Face 2 for Extrusion" (or similar) appears as a status message. The block type in Object Mode now shows EXTRUDE.
5. In Object Mode, set the **Extrude Axis** (X, Y, or Z) and **Extrude Distance** in the panel.
### Revolve from a Quad Face
Same as extrude — select a quad face, click **Tag as Revolve Block**. Then set:
- **Revolve Angle** (degrees)
- **Revolve Axis** (X/Y/Z)
- **Revolve Origin** (the point the face sweeps around)
### Loft Between Two Faces
1. In Edit Mode, select exactly **two quad faces** (hold Shift to select both).
2. Click **Tag as Loft Block**.
**✓ Checkpoint:** "Tagged Faces 0 and 3 for Lofting" (or similar).
---
## Part 6: The 2D Sketch Tool (Draw → Extrude/Revolve)
The Sketch Tool lets you draw a profile directly in the viewport instead of selecting faces on a mesh.
### Draw a Sketch
1. In Object Mode, click **Draw Sketch** in the **Add Classy Primitives** section.
2. Your cursor changes — you are now in the sketch modal tool.
3. **Left-click** in the viewport to place points. Each click adds one point to the profile.
   - If your click hits an existing mesh object, the point snaps to that surface.
   - If not, the point falls onto the Z=0 plane.
   - Hold **Ctrl** while clicking to snap to the nearest 0.1m grid point.
4. When done, press **Enter** (or **Space**) to finalize.
5. Press **Escape** or **Right-click** to cancel.
**✓ Checkpoint:** A new `ClassySketch` Curve object appears in the Outliner. It should be selected automatically and become the active object.
> **Why exactly 4 points?** OpenFOAM's `blockMesh` uses hexahedral cells, which have 8 corners. An extruded or revolved block starts from a 4-vertex quad face — so the profile must have exactly 4 points to form a valid quad. The tool doesn't prevent you from placing fewer or more, but the downstream operators will warn you.
### Convert the Sketch
1. With the `ClassySketch` object selected, find the **Sketch Actions** box in the sidebar.
2. The box shows either:
   - **✓ Valid 4-Point Profile** — you're ready to proceed.
   - **⚠ Invalid Profile: Sketch has N points. Exactly 4 points required.** — you need to redo the sketch with exactly 4 points.
3. Click **Extrude Sketch** or **Revolve Sketch**.
**✓ Checkpoint:** A status message confirms the sketch was tagged. If you click the Extrude button with a 3-point sketch, you'll see "Sketch has 3 points. Extrude requires exactly 4 points." — this is a non-fatal warning; the pipeline will still try to build but will produce an `unsupported` spec entry (no block will be written).
---
## Part 7: Shape Chaining (Pipe Networks)
Chain Cylinder and Frustum blocks end-to-end to build a multi-segment pipe.
1. Add a Cylinder.
2. Add a second Cylinder (or Frustum).
3. Select the second cylinder.
4. In the **Shape Chaining** section, use the **Chain From** object picker to select the first cylinder.
5. Set **Chain Length** (the length of the new segment).
6. If using a Frustum for a taper, set **Chain Radius 2** (end radius).
**✓ Checkpoint:** When you run Generate, the pipeline does a two-pass build: the source cylinder is built first, then the chained cylinder starts at its end face. The resulting `blockMeshDict` has two adjacent hex blocks that share a face.
---
## Part 8: The Full Pipeline
Once your blocks are configured, run the full pipeline:
### One Click: ▶ Run All
Click the large **▶ Run All** button at the bottom of the panel. It runs:
1. **Generate blockMeshDict** — writes `system/blockMeshDict`.
2. **Run blockMesh** — runs the OpenFOAM mesher.
3. **Convert to VTK** — converts the result with `foamToVTK`.
4. **Reload in Blender** — loads the VTK back into Blender as a new mesh object.
**✓ Checkpoint after step 1:** Open `system/blockMeshDict` in a text editor — it should be a valid OF-format dictionary with a `blocks` list.
**✓ Checkpoint after step 2:** The sidebar shows "Last Quality: Non-ortho: X.X | Skewness: Y.YY". Non-orthogonality below 60° and skewness below 2 are generally considered good.
**✓ Checkpoint after step 4:** A new mesh object (named something like `BlockMesh_Result`) appears in the Outliner. It shows the structured hex mesh you generated.
### Step by Step
If the full pipeline fails, use the individual buttons at the bottom of the panel:
- **1. Generate blockMeshDict**
- **2. Run blockMesh**
- **3. Convert to VTK**
- **4. Reload in Blender**
Each step checks that the previous step's output exists before running. If blockMesh hasn't run yet, "Convert to VTK" will say "polyMesh not found — run blockMesh first."
---
## Troubleshooting
### "No Case Directory" popup
The **Case Path** field is empty. Set it in **Case Settings** before clicking any pipeline button.
### "No mesh objects found"
There are no MESH type objects in the scene (or all of them are set to **Exclude from Mesh**). Add at least one primitive block.
### "No supported structured mesh objects found"
All objects are marked as `unsupported` in the extractor. This usually means:
- The object's block type is set to something the extractor couldn't build a valid spec for (e.g., an EXTRUDE block where the tagged face has non-quad vertices).
- Check the system console for a traceback with more detail.
### The sketch always places points at Z=0, not on my mesh
The sketch raycasts against scene geometry using the WINDOW region of the 3D viewport. If the 3D viewport is not in focus when you invoked the sketch tool (e.g., you clicked the button from the sidebar), the region coordinates may be mismatched. Try:
- Click somewhere in the 3D viewport first to give it focus.
- Then use the panel button.
### Extrude/Revolve sketch produces "Unsupported" block (no geometry written)
The sketch has the wrong number of points. The `classy_blocks` library requires exactly 4 points to form a valid quad face. The **Sketch Actions** panel will show the point count with a warning. Re-draw the sketch with exactly 4 clicks.
### `classy_blocks` doesn't catch self-intersecting or non-planar profiles
The add-on validates that your sketch has exactly 4 points. It does **not** check whether those 4 points form a valid non-self-intersecting quad, or whether they are coplanar. If your 4 points cross each other or are 3D (not flat), `blockMesh` will accept the `blockMeshDict` but produce a degenerate or inverted mesh. Always verify the resulting mesh quality in Blender after reloading.
### blockMesh crashes with "Cannot find surface ... in geometry"
The STL file referenced in the projection is not in `constant/triSurface/`. Use the **Export as Terrain STL** button to copy it there automatically, or manually copy it.
### "STL file not found"
The path in the **STL File** field is a relative path that isn't resolving correctly. Use an absolute path, or use **Export as Terrain STL** to write the STL directly into the case.
### The Cylinder/Frustum spec is wrong after applying rotations
Do not apply `Ctrl+A → Rotation` to Cylinder, Frustum, or ExtrudedRing objects. The extractor reads their bounding box in local Z-up space; applying rotations rotates the local frame and makes the bounding box no longer match the geometry. If you need to reorient a cylinder, use the Transform properties to set the object's location and rotation, but **do not apply** the rotation.
### Auto-Update keeps regenerating
If **Auto-Update Mesh** is enabled, any scene change (including moving the reloaded mesh) can trigger a regenerate. Either disable auto-update while adjusting the scene, or increase the block limit in Add-on Preferences.