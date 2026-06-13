"""
addon/vtk_importer.py
Reads VTK mesh files (produced by foamToVTK) and creates Blender mesh objects.

This is Phase 7 of the pipeline: VTK → Blender mesh data.
After blockMesh creates the mesh and foamToVTK converts it to VTK format,
this module uses PyVista to read the VTK file and reconstruct the mesh
as a Blender object — completing the feedback loop.

REQUIRES: pyvista (installed in Blender's Python)
REQUIRES: bpy (Blender Python — cannot be run standalone)

DATA FLOW:
  foamToVTK → case_dir/VTK/*.vtk → [this module] → Blender mesh object

CALLED BY: operators.py → CLASSY_OT_reload_mesh.execute()
"""

import os
import glob

import bpy
try:
    import pyvista as pv
except ImportError:
    pv = None  # Handled gracefully by dependencies check


def find_vtk_files(case_path):
    """
    Searches for VTK files in the case directory's VTK/ subfolder.

    foamToVTK creates files like:
      case_dir/VTK/case_name_0.vtk
      or case_dir/VTK/internal.vtu

    Args:
        case_path: Path to the OpenFOAM case directory.

    Returns:
        list: Sorted list of absolute paths to VTK files found.
              Empty list if no files found.
    """
    vtk_patterns = [
        os.path.join(case_path, "VTK", "*.vtu"),
        os.path.join(case_path, "VTK", "*.vtk"),
        os.path.join(case_path, "VTK", "**", "*.vtu"),
        os.path.join(case_path, "VTK", "**", "*.vtk"),
    ]
    vtk_files = []
    for pattern in vtk_patterns:
        vtk_files.extend(glob.glob(pattern, recursive=True))
    return sorted(set(vtk_files))


def load_vtk_as_blender_mesh(vtk_path, mesh_name="BlockMesh_Result"):
    """
    Reads a VTK file with PyVista and creates a Blender mesh object.

    The resulting object appears in Blender's viewport as a mesh that
    the user can inspect, rotate, and examine in edit mode to verify
    the block topology.

    Args:
        vtk_path: Absolute path to a .vtk or .vtu file.
        mesh_name: Name for the created Blender object (default: "BlockMesh_Result").

    Returns:
        The created Blender object, or None on failure.
    """
    # 1. Load VTK file with PyVista
    try:
        pv_mesh = pv.read(vtk_path)
    except Exception as e:
        raise RuntimeError(
            f"Failed to read VTK file: {vtk_path}\n"
            f"PyVista error: {e}\n"
            "Check that the file exists and is a valid VTK/VTU format."
        )

    # 2. Extract the surface (boundary faces) from the volume mesh
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        surface = pv_mesh.extract_surface()

    # 3. Check for empty surface
    if surface.n_cells == 0:
        raise RuntimeError(
            f"VTK file has 0 surface faces: {vtk_path}\n"
            "The mesh may be volume-only with no extractable surface, "
            "or the file may be empty."
        )

    # 4. Log mesh statistics
    print(f"[vtk_importer] Loading: {vtk_path}")
    print(f"[vtk_importer]   Volume: {pv_mesh.n_points} points, {pv_mesh.n_cells} cells")
    print(f"[vtk_importer]   Surface: {surface.n_points} points, {surface.n_cells} faces")

    # Split into disconnected bodies (may fail on some VTK grid types)
    try:
        bodies = surface.split_bodies()
        if len(bodies) == 0:
            bodies = [surface]
    except (AttributeError, RuntimeError, Exception) as e:
        print(f"[vtk_importer]   split_bodies() failed ({e}), treating as single body")
        bodies = [surface]
    
    # Remove old objects
    _remove_existing_objects_with_prefix(mesh_name)

    created_objs = []
    for i, body in enumerate(bodies):
        if body.n_cells == 0:
            continue
            
        vertices = [tuple(v) for v in body.points.tolist()]
        # UnstructuredGrid has cells, PolyData has faces
        try:
            faces = _parse_pyvista_faces(body.faces)
        except AttributeError:
            faces = _parse_pyvista_faces(body.cells)
        
        name = f"{mesh_name}_{i+1}" if len(bodies) > 1 else mesh_name
        
        blender_mesh = bpy.data.meshes.new(name)
        blender_mesh.from_pydata(vertices, [], faces)
        blender_mesh.update()
        
        obj = bpy.data.objects.new(name, blender_mesh)
        bpy.context.collection.objects.link(obj)
        
        obj.location = (0, 0, 0)
        obj.select_set(True)
        if hasattr(obj, "classy_block_props"):
            obj.classy_block_props.exclude_from_mesh = True
            
        created_objs.append(obj)
        print(f"[vtk_importer]   Created Blender object: '{name}' "
              f"({len(vertices)} verts, {len(faces)} faces)")

    if created_objs:
        bpy.context.view_layer.objects.active = created_objs[0]

    return created_objs[0] if created_objs else None


def _parse_pyvista_faces(pv_faces):
    """
    Converts PyVista's face array format to Blender's face format.

    PyVista stores faces as a flat array: [n_verts, v0, v1, ..., n_verts, v0, v1, ...]
    Blender's from_pydata expects a list of tuples: [(v0, v1, v2, v3), ...]

    Handles both triangles (n=3) and quads (n=4), as well as any polygon.

    Args:
        pv_faces: PyVista face array (numpy array or list).

    Returns:
        list: List of face tuples, e.g. [(0, 1, 2, 3), (4, 5, 6, 7), ...]
    """
    faces = []
    i = 0
    total = len(pv_faces)

    while i < total:
        n = int(pv_faces[i])  # number of vertices in this face
        if n < 3:
            # Skip degenerate faces (edges or points)
            i += n + 1
            continue
        face = tuple(int(pv_faces[i + 1 + j]) for j in range(n))
        faces.append(face)
        i += n + 1

    return faces


def _remove_existing_objects_with_prefix(prefix):
    """
    Removes all existing Blender objects and their mesh data whose names start
    with the given prefix. Used to clean up before re-importing the mesh.

    Args:
        prefix: Name prefix of the Blender objects to remove.
    """
    objs_to_remove = [obj for obj in bpy.data.objects if obj.name.startswith(prefix)]
    
    for obj in objs_to_remove:
        mesh_data = obj.data if obj.type == 'MESH' else None

        obj_name = obj.name
        
        # Unlink from all collections
        for collection in obj.users_collection:
            collection.objects.unlink(obj)

        # Remove the object
        bpy.data.objects.remove(obj, do_unlink=True)

        # Remove orphan mesh data
        if mesh_data and mesh_data.users == 0:
            bpy.data.meshes.remove(mesh_data)

        print(f"[vtk_importer]   Removed existing object: '{obj_name}'")
