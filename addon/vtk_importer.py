# addon/vtk_importer.py
# Reads VTK mesh files (produced by foamToVTK) and creates Blender mesh objects.
#
# This is Phase 7 of the pipeline: VTK → Blender mesh data.
# After blockMesh creates the mesh and foamToVTK converts it to VTK format,
# this module uses PyVista to read the VTK file and reconstruct the mesh
# as a Blender object — completing the feedback loop.
#
# REQUIRES: pyvista (installed in Blender's Python)
# REQUIRES: bpy (Blender Python — cannot be run standalone)
#
# DATA FLOW:
#   foamToVTK → case_dir/VTK/*.vtk → [this module] → Blender mesh object
#
# CALLED BY: operators.py → CLASSY_OT_reload_mesh.execute()

import os
import glob

import bpy
import pyvista as pv


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
    surface = pv_mesh.extract_surface()

    # 3. Check for empty surface
    if surface.n_cells == 0:
        raise RuntimeError(
            f"VTK file has 0 surface faces: {vtk_path}\n"
            "The mesh may be volume-only with no extractable surface, "
            "or the file may be empty."
        )

    # 4. Log mesh statistics for debugging (visible in Blender System Console)
    print(f"[vtk_importer] Loading: {vtk_path}")
    print(f"[vtk_importer]   Volume: {pv_mesh.n_points} points, {pv_mesh.n_cells} cells")
    print(f"[vtk_importer]   Surface: {surface.n_points} points, {surface.n_cells} faces")
    print(f"[vtk_importer]   Bounds: {[round(b, 4) for b in surface.bounds]}")

    # 5. Extract vertices (Nx3 numpy → list of tuples for Blender)
    vertices = [tuple(v) for v in surface.points.tolist()]

    # 6. Extract and parse faces
    # PyVista >= 0.38 uses .get_connectivity_and_offset() but .faces still works
    raw_faces = surface.faces
    faces = _parse_pyvista_faces(raw_faces)

    print(f"[vtk_importer]   Parsed {len(vertices)} vertices, {len(faces)} faces")

    # 7. Remove any existing object with the same name (for re-import)
    _remove_existing_object(mesh_name)

    # 8. Create Blender mesh data
    blender_mesh = bpy.data.meshes.new(mesh_name)
    blender_mesh.from_pydata(vertices, [], faces)
    blender_mesh.update()

    # 9. Create Blender object and link to active collection
    obj = bpy.data.objects.new(mesh_name, blender_mesh)
    bpy.context.collection.objects.link(obj)

    # 10. Set location to world origin and make active
    obj.location = (0, 0, 0)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    print(f"[vtk_importer]   Created Blender object: '{mesh_name}' "
          f"({len(vertices)} verts, {len(faces)} faces)")

    return obj


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


def _remove_existing_object(name):
    """
    Removes an existing Blender object and its mesh data if present.
    Used to clean up before re-importing the mesh.

    Args:
        name: Name of the Blender object to remove.
    """
    if name not in bpy.data.objects:
        return

    obj = bpy.data.objects[name]
    mesh_data = obj.data if obj.type == 'MESH' else None

    # Unlink from all collections
    for collection in obj.users_collection:
        collection.objects.unlink(obj)

    # Remove the object
    bpy.data.objects.remove(obj, do_unlink=True)

    # Remove orphan mesh data
    if mesh_data and mesh_data.users == 0:
        bpy.data.meshes.remove(mesh_data)

    print(f"[vtk_importer]   Removed existing object: '{name}'")
