"""
addon/geometry_extractor.py
Reads Blender scene objects and builds a spec dict for mesh_builder.

SUPPORTED BLOCK TYPES:
  - BOX:     bounding box → cb.Box(p_min, p_max)
    - Simple cubes (8 verts, 6 quad faces): clean hex mesh, no projection
    - Complex shapes (cylinders, cones, etc.): bounding box + STL self-projection
      to conform the mesh to the original shape
  - EXTRUDE: quad face + vector → cb.Extrude(face, vector)
  - REVOLVE: quad face + angle/axis/origin → cb.Revolve(face, angle, axis, origin)

STL SELF-PROJECTION:
  For shapes that are NOT simple cubes, the pipeline:
    1. Exports the object as STL to constant/triSurface/
    2. Creates a cb.Box bounding box
    3. Projects ALL 6 faces onto the object's own STL
    4. blockMesh snaps boundary vertices to the original shape surface

COORDINATE PRESERVATION:
  All coordinates are extracted in absolute world space using obj.matrix_world.

CALLED BY: operators.py → CLASSY_OT_generate_mesh.execute()
"""

import os


def extract_geometry(context):
    """
    Main entry point. Iterates all mesh objects, dispatches by block_type.

    Returns:
        {
            "blocks": [ { spec dict per block } ],
            "merge_tolerance": 1e-4,
        }
    """
    blocks = []

    for obj in context.scene.objects:
        if obj.type != 'MESH':
            continue

        props = getattr(obj, "classy_block_props", None)

        # Exclude check
        if props and getattr(props, "exclude_from_mesh", False):
            print(f"[classy_blocks] Skipping '{obj.name}' (excluded)")
            continue

        block_type = getattr(props, "block_type", "BOX") if props else "BOX"

        try:
            if block_type == "BOX":
                spec = _extract_box(obj, props)
            elif block_type == "EXTRUDE":
                spec = _extract_extrude(obj, props)
            elif block_type == "REVOLVE":
                spec = _extract_revolve(obj, props)
            else:
                print(f"[classy_blocks] Unknown block type '{block_type}' "
                      f"for '{obj.name}', skipping")
                continue

            blocks.append(spec)
            proj_status = ""
            if spec.get("needs_self_projection"):
                proj_status = " (will project to own STL)"
            print(f"[classy_blocks] Extracted {block_type} block: "
                  f"'{obj.name}'{proj_status}")

        except Exception as e:
            print(f"[classy_blocks] ERROR extracting '{obj.name}': {e}")
            import traceback; traceback.print_exc()
            continue

    print(f"[classy_blocks] Total blocks extracted: {len(blocks)}")
    return {
        "blocks": blocks,
        "merge_tolerance": 1e-4,
    }


# ─────────────────────── EXTRACTORS ───────────────────────


def _extract_box(obj, props):
    """
    BOX: use world-space bounding box.

    For simple cubes (8 verts, 6 quad faces): clean hex mesh, no projection.
    For complex shapes: sets needs_self_projection=True so the pipeline
    exports the object as STL and projects the box faces onto it.
    """
    p_min, p_max = _get_world_bounding_box(obj)
    cells = _read_cells(props)

    spec = {
        "type": "box",
        "name": obj.name,
        "p_min": p_min,
        "p_max": p_max,
        "cells": cells,
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
    }

    # Check if this is a simple cube or a complex shape needing projection
    is_simple = _is_box_shaped(obj)
    if not is_simple:
        stl_name = f"{obj.name}.stl"
        spec["needs_self_projection"] = True
        spec["self_stl_name"] = stl_name
        print(f"[classy_blocks]   '{obj.name}' is NOT a simple box → "
              f"will self-project onto '{stl_name}'")
    else:
        spec["needs_self_projection"] = False
        print(f"[classy_blocks]   '{obj.name}' is a simple box → "
              f"clean hex, no projection")

    # Optional user-specified single-face STL projection (terrain)
    if props:
        stl_file = getattr(props, "stl_file", "") or ""
        if stl_file:
            face_name = getattr(props, "stl_projection_face", "top")
            if "stl_projections" not in spec:
                spec["stl_projections"] = {}
            spec["stl_projections"][face_name] = os.path.basename(stl_file)
            print(f"[classy_blocks]   User STL projection: "
                  f"'{face_name}' → '{os.path.basename(stl_file)}'")

    return spec


def _extract_extrude(obj, props):
    """
    EXTRUDE: extract a quad face from the object and an extrusion vector.
    """
    face_index = getattr(props, "extrude_face_index", 0) if props else 0
    face_verts = _extract_face_vertices_world(obj, face_index)

    if len(face_verts) != 4:
        raise ValueError(
            f"Extrude face {face_index} on '{obj.name}' has "
            f"{len(face_verts)} vertices — must be exactly 4 (a quad). "
            f"Select a different face index."
        )

    extrude_axis_name = getattr(props, "extrude_axis", "Z") if props else "Z"
    distance = getattr(props, "extrude_distance", 1.0) if props else 1.0

    axis_map = {"X": [1, 0, 0], "Y": [0, 1, 0], "Z": [0, 0, 1]}
    axis_vec = axis_map.get(extrude_axis_name, [0, 0, 1])
    extrude_vector = [v * distance for v in axis_vec]

    return {
        "type": "extrude",
        "name": obj.name,
        "face": face_verts,
        "extrude_vector": extrude_vector,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
    }


def _extract_revolve(obj, props):
    """
    REVOLVE: extract a quad face and revolve parameters.
    """
    face_index = getattr(props, "revolve_face_index", 0) if props else 0
    face_verts = _extract_face_vertices_world(obj, face_index)

    if len(face_verts) != 4:
        raise ValueError(
            f"Revolve face {face_index} on '{obj.name}' has "
            f"{len(face_verts)} vertices — must be exactly 4."
        )

    angle_deg = getattr(props, "revolve_angle", 90.0) if props else 90.0
    axis_name = getattr(props, "revolve_axis", "Z") if props else "Z"
    origin = list(getattr(props, "revolve_origin", (0, 0, 0))) if props else [0, 0, 0]

    axis_map = {"X": [1, 0, 0], "Y": [0, 1, 0], "Z": [0, 0, 1]}
    axis_vec = axis_map[axis_name]

    return {
        "type": "revolve",
        "name": obj.name,
        "face": face_verts,
        "angle_deg": angle_deg,
        "axis": axis_vec,
        "origin": origin,
        "cells": _read_cells(props),
        "patch_name": _read_patch_name(props),
        **_read_grading(props),
    }


# ─────────────────────── HELPERS ───────────────────────


def _is_box_shaped(obj):
    """
    Returns True if the object is a simple axis-aligned cuboid.

    A simple box in Blender has exactly 8 vertices and 6 quad faces.
    Anything else (cylinder, cone, sphere, torus, monkey, etc.) returns False
    and will be handled via STL self-projection to preserve its shape.
    """
    import bpy
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data

    n_verts = len(mesh.vertices)
    n_faces = len(mesh.polygons)

    if n_verts != 8 or n_faces != 6:
        return False

    # All faces must be quads
    for poly in mesh.polygons:
        if len(poly.vertices) != 4:
            return False

    return True


def _get_world_bounding_box(obj):
    """
    Returns (p_min, p_max) for a Blender object in absolute world space.

    Uses obj.bound_box (8 corners in local space) and multiplies
    by obj.matrix_world to convert to world space.

    CRITICAL: obj.bound_box returns bpy_prop_array items, NOT Vector objects.
    Must wrap each corner in mathutils.Vector() before matrix multiplication.

    CRITICAL: Preserves actual Blender world-space coordinates.
    If a block is placed at (10,10,10), p_min/p_max will reflect that.
    """
    from mathutils import Vector

    world_corners = []
    for corner in obj.bound_box:
        # bound_box corners are bpy_prop_array — must convert to Vector
        local_vec = Vector(corner)
        world_co = obj.matrix_world @ local_vec
        world_corners.append(world_co)

    xs = [c[0] for c in world_corners]
    ys = [c[1] for c in world_corners]
    zs = [c[2] for c in world_corners]

    p_min = [min(xs), min(ys), min(zs)]
    p_max = [max(xs), max(ys), max(zs)]

    return p_min, p_max


def _extract_face_vertices_world(obj, face_index):
    """
    Returns a list of [x, y, z] world-space coordinates for a face's vertices.

    Uses depsgraph to get the evaluated mesh (applies modifiers).
    """
    import bpy
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data

    if face_index >= len(mesh.polygons):
        raise IndexError(
            f"Face index {face_index} out of range — object '{obj.name}' "
            f"has only {len(mesh.polygons)} faces."
        )

    poly = mesh.polygons[face_index]
    verts_world = []
    for vi in poly.vertices:
        co_local = mesh.vertices[vi].co
        co_world = obj.matrix_world @ co_local
        verts_world.append([co_world.x, co_world.y, co_world.z])

    return verts_world


def _read_cells(props):
    raw = getattr(props, "cells", None) if props else None
    if raw and len(raw) >= 3:
        return [max(1, int(raw[i])) for i in range(3)]
    return [10, 10, 10]


def _read_patch_name(props):
    return getattr(props, "patch_name", "defaultWall") if props else "defaultWall"


def _read_grading(props):
    gt = getattr(props, "grading_type", "RATIO") if props else "RATIO"
    raw_g = getattr(props, "grading", None) if props else None
    grading = [float(raw_g[i]) for i in range(3)] if raw_g and len(raw_g) >= 3 else [1.0, 1.0, 1.0]
    return {
        "grading_type": gt,
        "grading": grading,
        "start_size": float(getattr(props, "start_size", 1e-4) if props else 1e-4),
        "end_size": float(getattr(props, "end_size", 1e-4) if props else 1e-4),
    }
