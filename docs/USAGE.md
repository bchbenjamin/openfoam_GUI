# Classy FOAM User Manual

Welcome to the **Classy FOAM** (Classy Blocks Integration) add-on! This manual is designed for CFD engineers and meshers who want to build high-quality, structured hexahedral meshes without dealing with code. 

Using standard CAD workflows directly inside Blender, you can build parametric flow domains, snap pipes together, define boundary patches, and compile OpenFOAM `blockMesh` grids with the click of a button.

---

## 1. Setup & Physics (The Environment)

Before you start drawing your mesh, you need to tell the add-on where to save the mesh and what physics it belongs to.

### OpenFOAM Tutorials
If you don't already have an OpenFOAM case set up, you can grab one of the official templates:
1. Open the **OpenFOAM Tutorials** panel in the 3D Viewport side-bar.
2. Use the search bar to find a solver (e.g., `simpleFoam` or `icoFoam`).
3. Select a tutorial case from the list.
4. Click **Copy Tutorial to FOAM_RUN**. This will create a fresh folder in your workspace containing all the physics files (`controlDict`, `fvSchemes`, etc.) required to run a simulation.

### Case Directory
At the top of the main **Classy Blocks** panel, you will find the **Case Directory** field. 
- Point this to the OpenFOAM folder where you want your mesh saved. 
- If you used the Tutorial Manager, point this to the folder you just created.

---

## 2. Block Settings (Building the Grid)

You build your mesh using standard Blender shapes (like Cubes or Cylinders). When you select an object in Object Mode, the **Classy Blocks** panel will reveal its meshing settings.

### Base Settings
- **Exclude from Mesh (Checkbox):** Sometimes you want a reference object in your scene that isn't part of the fluid mesh. Check this box to ignore the object during mesh generation.
- **Cells (X, Y, Z):** Controls the density of the grid inside this specific block. Higher numbers mean a finer mesh.
- **Patch Name:** The default OpenFOAM boundary name (e.g., `defaultWall`) applied to the outer skin of this block.
- **Block Type:** Tells the mesher what shape you are trying to build. Choose `Box` for rectangular domains, `Cylinder` for straight pipes, `Frustum` for tapered pipes/nozzles, or use the advanced CAD tools below.

---

## 3. Advanced CAD Tools

For complex shapes, standard boxes and cylinders aren't enough. You can draw flat 2D cross-sections (like a single square face) and pull them into 3D shapes.

1. **Extrude:** 
   - In Edit Mode, select a single flat quad face.
   - Under **2D Sketch Tools**, click **Tag as Extrude Block**. 
   - Back in Object Mode, define the Extrude Axis (X, Y, or Z) and Distance. This pulls the flat 2D sketch into a 3D block along a straight line.
   
2. **Revolve:** 
   - In Edit Mode, select a single flat quad face.
   - Click **Tag as Revolve Block**.
   - In Object Mode, define the sweep angle (e.g., 90 degrees) and the rotation axis. This sweeps the flat face around a center point to create curved pipes or donuts.

3. **Multi-Block Lofting:**
   - Draw two separated 2D faces within the same object.
   - Select both faces in Edit Mode.
   - Click **Tag as Loft Block**.
   - The mesher will automatically stretch a smooth 3D block bridging the gap between those two faces.

---

## 4. Connecting Blocks (Pipe Networks)

If you are building a piping system with multiple cylinders, manually lining them up perfectly is tedious and prone to errors. Instead, use **Shape Chaining**.

1. Create your primary Cylinder.
2. Create a second Cylinder, and select it.
3. Under the **Shape Chaining (Pipe Networks)** section, click the **Chain From** box and select your primary Cylinder.
4. Specify a **Chain Length** and **End Radius**. 
5. The mesher will automatically snap the new pipe perfectly onto the end of the primary pipe, ensuring the grid flows flawlessly between them.

---

## 5. Boundary Conditions

In CFD, you must define where the fluid enters (Inlet), exits (Outlet), and hits solid walls. 

1. Scroll down to the **Boundary Conditions** panel in Object Mode.
2. Click **Add Boundary**.
3. **Side Name:** Tell the mesher which side of the block you are labelling. Look at the "Valid Sides" hint above the button to see what sides are available for your current shape (e.g., type `bottom`, `top`, `left`, or `outer`).
4. **Patch Name:** The name OpenFOAM will use (e.g., `inlet1`).
5. **Patch Type:** The mathematical condition for OpenFOAM. Choose `patch` for flow inlets/outlets, `wall` for solid surfaces, or `symmetry` for mirror planes.

---

## 6. Terrain Projection

If you are modeling wind flow over a landscape, you want the bottom of your mesh to hug the uneven ground.

1. Set your Block Type to **Box**.
2. Scroll to the **STL Face Projection** panel.
3. Choose which face to project downward (usually `bottom`).
4. Select your `.stl` terrain file. 
5. The mesher will cast the bottom of the structured box onto the bumpy terrain while keeping the sky above it perfectly flat.

*(Tip: You can use the **Export as Terrain STL** button under Terrain Utilities to save a Blender landscape object as an STL file for this exact purpose.)*

---

## 7. Execution

Once your blocks and boundaries are set, you are ready to compile the mesh!

### Grading
Before executing, you can check the **Grading** panel. This allows you to bias the mesh spacing. For example, using **Start Size** lets you squash the grid cells very tightly against a wall to accurately capture boundary layer friction, while leaving the center of the flow domain coarse to save simulation time.

### Generating the Mesh
At the bottom of the panel, you will find the pipeline controls:

- **▶ Run All:** The easiest option. Clicking this master button will extract your Blender geometry, generate the OpenFOAM `blockMeshDict`, execute the OpenFOAM mesh generation in the background, convert the results, and pop the final grid back into your Blender viewport so you can inspect it.
- **Auto-Update Mesh:** Toggle this on to automatically re-run the pipeline in the background every time you tweak a vertex or change a setting. This provides real-time, instant feedback on your mesh quality.
- **Individual Steps (1-4):** If you are debugging a complex case, you can run the pipeline step-by-step (Generate -> Run -> Convert -> Reload) to see exactly where a failure occurs.

After generation, check the **Last Quality** readout above the Run button. If your Non-Orthogonality and Skewness values look healthy, your mesh is ready to solve!
