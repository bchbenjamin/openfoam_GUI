"""
addon/geometry_extractor.py
Extracts geometry from Blender objects and converts them into
a spec dict that mesh_builder.build_from_spec() can consume.

This module is the bridge between Blender's 3D scene data and
classy_blocks' Python API. It reads Blender objects (cubes, extruded
faces, etc.), extracts their world-space coordinates and custom
properties (cell counts, patch names, block type), and packages
them into the spec dict format documented in mesh_builder.py.

REQUIRES BLENDER PYTHON (bpy) — cannot be run standalone.

SPEC DICT FORMAT (output of extract_geometry()):
  {
    "blocks": [
      {
        "type": "box",            # "box", "extrude", or "revolve"
        "name": "Cube",           # Blender object name
        "p_min": [x, y, z],       # minimum corner (world space)
        "p_max": [x, y, z],       # maximum corner (world space)
        "cells": [10, 10, 10],    # cell count per axis
        "grading": [1.0, 1.0, 1.0],  # expansion ratios
        "patch_name": "wall",     # boundary patch name
      },
      ...
    ],
    "merge_tolerance": 1e-4
  }

CALLED BY: operators.py → CLASSY_OT_generate_mesh.execute()
"""

import bpy
from mathutils import Vector


def extract_geometry(context):
    """
    Scans all objects in the current Blender scene, finds those tagged
    as mesh blocks (via classy_block_props.is_block), and extracts their
    geometry into a spec dict for mesh_builder.build_from_spec().

    Args:
        context: Blender context (bpy.context), passed from an operator.

    Returns:
        dict: Spec dict with "blocks" list and "merge_tolerance".
              Returns {"blocks": [], "merge_tolerance": 1e-4} if no
              tagged objects are found.
    """
    blocks = []

    for obj in context.scene.objects:
        # Skip non-mesh objects
        if obj.type != 'MESH':
            continue

        props = getattr(obj, "classy_block_props", None)
        
        # Check exclusion toggle
        if props and getattr(props, "exclude_from_mesh", False):
            continue

        block_type = getattr(props, "block_type", "box") if props else "box"

        # Read cells with safe access — ensure 3-element list
        raw_cells = getattr(props, "cells", None) if props else None
        if raw_cells is not None and len(raw_cells) >= 3:
            cells = [max(1, int(raw_cells[i])) for i in range(3)]
        else:
            cells = [10, 10, 10]

        # Read grading with safe access — default to uniform
        raw_grading = getattr(props, "grading", None) if props else None
        if raw_grading is not None and len(raw_grading) >= 3:
            grading = [float(raw_grading[i]) for i in range(3)]
        else:
            grading = [1.0, 1.0, 1.0]

        patch_name = getattr(props, "patch_name", "defaultWall") if props else "defaultWall"
        patch_name = patch_name or "defaultWall"

        # Read grading type and size parameters
        grading_type = getattr(props, "grading_type", "RATIO") if props else "RATIO"
        start_size = getattr(props, "start_size", 1e-4) if props else 1e-4
        end_size = getattr(props, "end_size", 1e-4) if props else 1e-4

        # Read STL projection (only relevant for box blocks)
        stl_file = getattr(props, "stl_file", "") if props else ""
        stl_projection_face = getattr(props, "stl_projection_face", "top") if props else "top"

        # Dispatch by block type
        try:
            if block_type == "box":
                block_spec = _extract_box(obj, cells, grading, patch_name,
                                          grading_type, start_size, end_size,
                                          stl_file, stl_projection_face)
            elif block_type == "extrude":
                block_spec = _extract_extrude(obj, props, cells, grading, patch_name,
                                              grading_type, start_size, end_size)
            elif block_type == "revolve":
                block_spec = _extract_revolve(obj, props, cells, grading, patch_name,
                                              grading_type, start_size, end_size)
            else:
                print(f"[classy_blocks] WARNING: Unknown block_type "
                      f"'{block_type}' on '{obj.name}' — skipping")
                continue

            blocks.append(block_spec)
            print(f"[classy_blocks] Extracted {block_type} block: '{obj.name}'")

        except Exception as e:
            print(f"[classy_blocks] ERROR extracting '{obj.name}': {e}")
            continue

    return {
        "blocks": blocks,
        "merge_tolerance": 1e-4,
    }


def _get_world_bounding_box(obj):
    """
    Returns (p_min, p_max) for a Blender object in absolute world space.

    Uses obj.bound_box (8 corners in local space) and multiplies
    by obj.matrix_world to convert to world space.

    CRITICAL: Preserves Blender's world coordinates exactly.
    If a block is at (10, 10, 10) in Blender, the returned p_min/p_max
    will reflect (10, 10, 10), NOT (0, 0, 0) relative.

    Args:
        obj: A Blender object (bpy.types.Object).

    Returns:
        tuple: ([x_min, y_min, z_min], [x_max, y_max, z_max]) as plain lists.
    """
    # obj.bound_box is 8 corners in local space
    # matrix_world transforms local → absolute world coordinates
    world_coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    p_min = [min(co[i] for co in world_coords) for i in range(3)]
    p_max = [max(co[i] for co in world_coords) for i in range(3)]

    return (p_min, p_max)


def _extract_box(obj, cells, grading, patch_name,
                 grading_type="RATIO", start_size=1e-4, end_size=1e-4,
                 stl_file="", stl_projection_face="top"):
    """
    Extracts a box block spec from a Blender object using its
    world-space bounding box.

    Args:
        obj: A Blender mesh object tagged as a "box" block.
        cells: [nx, ny, nz] cell counts.
        grading: [gx, gy, gz] expansion ratios.
        patch_name: Boundary patch name string.
        grading_type: "RATIO", "START_SIZE", or "SYMMETRIC".
        start_size: First cell size in meters.
        end_size: Last cell size in meters.
        stl_file: Path to an STL file for face projection.
        stl_projection_face: Which face to project onto the STL.

    Returns:
        dict: Block spec dict.
    """
    p_min, p_max = _get_world_bounding_box(obj)

    spec = {
        "type": "box",
        "name": obj.name,
        "p_min": p_min,
        "p_max": p_max,
        "cells": cells,
        "grading": grading,
        "grading_type": grading_type,
        "start_size": float(start_size),
        "end_size": float(end_size),
        "patch_name": patch_name,
    }

    # Add STL projection if an STL file is set
    if stl_file:
        import os
        spec["stl_projections"] = {
            stl_projection_face: os.path.basename(stl_file)
        }

    return spec


def _extract_face_vertices(obj, face_index=0):
    """
    Extracts the world-space vertices of a quadrilateral face.
    Used for "extrude" and "revolve" block types.

    CRITICAL: Uses obj.matrix_world to ensure absolute world-space
    coordinates are preserved. A face at (10, 10, 10) in Blender
    will return vertices at (10, 10, 10), not relative to origin.

    Args:
        obj: A Blender mesh object.
        face_index: Index of the face to extract (default: 0).

    Returns:
        list: [[x,y,z], [x,y,z], ...] — vertices in world space.

    Raises:
        ValueError: If the face doesn't exist or has fewer than 3 vertices.
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh_data = eval_obj.to_mesh()

    try:
        if face_index >= len(mesh_data.polygons):
            raise ValueError(
                f"Face index {face_index} out of range — "
                f"'{obj.name}' has {len(mesh_data.polygons)} faces"
            )

        face = mesh_data.polygons[face_index]

        if len(face.vertices) < 3:
            raise ValueError(
                f"Face {face_index} on '{obj.name}' has only "
                f"{len(face.vertices)} vertices (need at least 3)"
            )

        # Apply matrix_world to get absolute world coordinates
        verts = []
        for vi in face.vertices:
            world_co = obj.matrix_world @ mesh_data.vertices[vi].co
            verts.append([world_co.x, world_co.y, world_co.z])

        return verts
    finally:
        eval_obj.to_mesh_clear()


def _extract_extrude(obj, props, cells, grading, patch_name,
                     grading_type="RATIO", start_size=1e-4, end_size=1e-4) -> dict:
    """
    Extracts an extrude block spec from a Blender object.

    Extrude blocks are defined by a base face and an extrusion vector.
    The base face's 4 vertices are extracted in world space.
    The extrude vector is taken from the object's Z-dimension by default,
    or from a custom property if set.

    Args:
        obj: A Blender mesh object tagged as an "extrude" block.
        props: The object's classy_block_props.
        cells: [nx, ny, nz] cell counts.
        grading: [gx, gy, gz] expansion ratios.
        patch_name: Boundary patch name string.
        grading_type: "RATIO", "START_SIZE", or "SYMMETRIC".
        start_size: First cell size in meters.
        end_size: Last cell size in meters.

    Returns:
        dict: Block spec dict.
    """
    face_index = getattr(props, "extrude_face_index", 0) or 0
    face_verts = _extract_face_vertices(obj, face_index)

    # Get extrude vector — use custom property if set, else compute
    # from the object's local Z axis scaled by its Z dimension
    raw_extrude = getattr(props, "extrude_vector", None)
    if raw_extrude is not None and len(raw_extrude) >= 3:
        extrude_vector = [float(raw_extrude[i]) for i in range(3)]
    else:
        # Default: extrude along the object's local Z axis
        # Use the object's bounding box to determine the height
        p_min, p_max = _get_world_bounding_box(obj)
        height = p_max[2] - p_min[2]
        if height < 1e-10:
            height = 1.0  # fallback for flat objects
        # Transform the local Z direction to world space
        local_z = obj.matrix_world.to_3x3() @ Vector((0, 0, 1))
        local_z.normalize()
        extrude_vector = [local_z.x * height, local_z.y * height, local_z.z * height]

    return {
        "type": "extrude",
        "name": obj.name,
        "face": face_verts,
        "extrude_vector": extrude_vector,
        "cells": cells,
        "grading": grading,
        "grading_type": grading_type,
        "start_size": float(start_size),
        "end_size": float(end_size),
        "patch_name": patch_name,
    }


def _extract_revolve(obj, props, cells, grading, patch_name,
                     grading_type="RATIO", start_size=1e-4, end_size=1e-4) -> dict:
    """
    Extracts a revolve block spec from a Blender object.

    Revolve blocks are defined by a base face, a rotation angle,
    an axis vector, and an origin point.

    Args:
        obj: A Blender mesh object tagged as a "revolve" block.
        props: The object's classy_block_props.
        cells: [nx, ny, nz] cell counts.
        grading: [gx, gy, gz] expansion ratios.
        patch_name: Boundary patch name string.
        grading_type: "RATIO", "START_SIZE", or "SYMMETRIC".
        start_size: First cell size in meters.
        end_size: Last cell size in meters.

    Returns:
        dict: Block spec dict.
    """
    face_index = getattr(props, "revolve_face_index", 0) or 0
    face_verts = _extract_face_vertices(obj, face_index)

    # Revolve angle in degrees (mesh_builder converts to radians)
    angle = getattr(props, "revolve_angle", 90.0) or 90.0

    # Revolve axis — default to Y axis [0, 1, 0]
    raw_axis = getattr(props, "revolve_axis", None)
    if raw_axis is not None and len(raw_axis) >= 3:
        axis = [float(raw_axis[i]) for i in range(3)]
    else:
        axis = [0.0, 1.0, 0.0]

    # Revolve origin — default to world origin [0, 0, 0]
    raw_origin = getattr(props, "revolve_origin", None)
    if raw_origin is not None and len(raw_origin) >= 3:
        origin = [float(raw_origin[i]) for i in range(3)]
    else:
        origin = [0.0, 0.0, 0.0]

    return {
        "type": "revolve",
        "name": obj.name,
        "face": face_verts,
        "angle": float(angle),
        "axis": axis,
        "origin": origin,
        "cells": cells,
        "grading": grading,
        "grading_type": grading_type,
        "start_size": float(start_size),
        "end_size": float(end_size),
        "patch_name": patch_name,
    }
