# Classy Blocks Integration: User Manual

Welcome to the **Classy Blocks Integration** Blender add-on. This tool transforms Blender into a Parametric Structured Mesh Builder for OpenFOAM CFD simulations. It leverages the `classy_blocks` Python API to generate mathematically rigorous, conformal hex-meshes using a CAD-like workflow.

Follow this workflow to set up, build, and execute a fully resolved OpenFOAM case.

---

## Step 1: Deploy Physics
Before building geometry, you need a valid OpenFOAM environment (`controlDict`, `fvSchemes`, `fvSolution`, etc.).
1. Open the **OpenFOAM Tutorials** panel in the 3D Viewport side-bar.
2. Search for a relevant template (e.g., `incompressible/simpleFoam/pitzDaily`).
3. Click **Copy Tutorial to FOAM_RUN**.
4. In the main Classy Blocks panel, set the **Case Directory** to this newly deployed folder.

---

## Step 2: Parametric Block Building
Build your fluid domain parametrically using primitives or 2D sketches. **Do not apply scale/rotation (Ctrl+A) to primitives**, as the backend mathematically extracts your local transforms.

* **Primitives (Object Mode):** Spawn a Blender Cube or Cylinder. In the Object properties panel, set its Block Type to `BOX`, `CYLINDER`, or `FRUSTUM`. Adjust its dimensions locally.
* **2D Sketch Extrusion (Edit Mode):** 
  1. Add a single quad face (Plane).
  2. Enter Edit Mode (`Tab`).
  3. Under **2D Sketch Tools**, click **Tag as Extrude Block** (or Revolve).
  4. Return to Object Mode and set the Extrude Vector (X, Y, Z) and Distance.
* **Multi-Block Lofting (Edit Mode):**
  1. Create two disjoint quad faces in the same mesh object.
  2. Select both faces.
  3. Click **Tag as Loft Block**. 
  4. The add-on will loft a 3D block seamlessly between them.

---

## Step 3: Conformal Chaining
To ensure perfectly conformal O-grids when building pipe networks, use the **Shape Chaining** tool rather than manually placing cylinders end-to-end.
1. Select a new block.
2. In the properties panel, check the **Shape Chaining (Pipe Networks)** section.
3. Set the **Chain From** source to an existing Cylinder or Frustum.
4. Specify the **Chain Length** and **End Radius**. The new block will parametrically lock onto the end face of the source block.

---

## Step 4: Boundary Conditions
Define OpenFOAM patches (Inlet, Outlet, Wall, etc.) directly on your parametric shapes. 
1. In Object Mode, scroll to the **Boundary Conditions** panel.
2. Click **Add Boundary**.
3. Choose the semantic side of the block you wish to label (e.g., `bottom`, `top`, `outer`). *The valid side names are dynamically hinted based on your selected block type.*
4. Enter the OpenFOAM **Patch Name** (e.g., `inlet`) and **Patch Type** (e.g., `patch`, `wall`, `symmetry`).
5. When the mesh compiles, these boundaries are perfectly mapped into the `blockMeshDict`.

---

## Step 5: STL Terrain Projection
Project a structured `BOX` block downwards to conform onto a triangulated landscape or complex surface.
1. Assign your primary block the `BOX` type.
2. In the **STL Face Projection** panel, select the face to project (e.g., `bottom`).
3. Select the target `.stl` file on disk. 
4. The generated blockMesh will project its bottom vertices perfectly onto the triangulated surface, maintaining a structured hexahedral topology above it.

---

## Step 6: Execution
Once your geometry, chaining, and boundaries are defined, compile the mesh:
1. Click **▶ Run All** at the bottom of the Classy Blocks panel.
2. The add-on will automatically:
   - Extract your parametric bounds and rotations.
   - Generate the `blockMeshDict` using the `classy_blocks` engine.
   - Execute OpenFOAM's `blockMesh` binary in the background.
   - Run `foamToVTK` to convert the mesh.
   - Import the result back into Blender's viewport for visual verification.
3. Review the reported **Last Quality** (Non-Orthogonality and Skewness) to ensure your mesh is ready for simulation!
