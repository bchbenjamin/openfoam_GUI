# addon/geometry_extractor.py
# Extracts geometry from Blender objects and converts them into
# a spec dict that mesh_builder.build_from_spec() can consume.
#
# This module is the bridge between Blender's 3D scene data and
# classy_blocks' Python API. It reads Blender objects (cubes, extruded
# faces, etc.), extracts their world-space coordinates and custom
# properties (cell counts, patch names, block type), and packages
# them into the spec dict format documented in mesh_builder.py.
#
# REQUIRES BLENDER PYTHON (bpy) — cannot be run standalone.
#
# SPEC DICT FORMAT (output of extract_geometry()):
#   {
#     "blocks": [
#       {
#         "type": "box",            # "box", "extrude", or "revolve"
#         "name": "Cube",           # Blender object name
#         "p_min": [x, y, z],       # minimum corner (world space)
#         "p_max": [x, y, z],       # maximum corner (world space)
#         "cells": [10, 10, 10],    # cell count per axis
#         "grading": [1.0, 1.0, 1.0],  # expansion ratios
#         "patch_name": "wall",     # boundary patch name
#       },
#       ...
#     ],
#     "merge_tolerance": 1e-4
#   }
#
# CALLED BY: operators.py → CLASSY_OT_generate_mesh.execute()

# TODO: Import bpy — only works inside Blender's Python environment
# import bpy


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

    How block types are extracted:
        - "box": Uses the object's bounding box (world space) to get p_min/p_max.
        - "extrude": TODO — extract the base face vertices and extrude vector.
        - "revolve": TODO — extract face, angle, axis, and origin.
    """
    # TODO: Implement — placeholder returns empty spec
    # Steps to implement:
    #   1. Iterate over context.scene.objects
    #   2. For each object with obj.classy_block_props.is_block == True:
    #      a. Get the evaluated object (with modifiers applied) via depsgraph
    #      b. Read block_type from obj.classy_block_props.block_type
    #      c. For "box": compute world-space bounding box → p_min, p_max
    #      d. For "extrude": extract 4-point base face + extrude vector
    #      e. For "revolve": extract face, angle, axis, origin
    #      f. Read cells from obj.classy_block_props.cells
    #      g. Read patch_name from obj.classy_block_props.patch_name
    #      h. Read grading (defaults to [1.0, 1.0, 1.0])
    #   3. Return the assembled spec dict
    return {
        "blocks": [],
        "merge_tolerance": 1e-4,
    }


def _get_world_bounding_box(obj):
    """
    Returns (p_min, p_max) for a Blender object in world space.

    Uses obj.bound_box (8 corners in local space) and multiplies
    by obj.matrix_world to convert to world space.

    Args:
        obj: A Blender object (bpy.types.Object).

    Returns:
        tuple: ([x_min, y_min, z_min], [x_max, y_max, z_max])
    """
    # TODO: Implement
    # Steps:
    #   1. world_coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    #   2. p_min = [min(co[i] for co in world_coords) for i in range(3)]
    #   3. p_max = [max(co[i] for co in world_coords) for i in range(3)]
    #   4. return (p_min, p_max)
    pass


def _extract_face_vertices(obj, face_index=0):
    """
    Extracts the 4 world-space vertices of a quadrilateral face.
    Used for "extrude" and "revolve" block types.

    Args:
        obj: A Blender mesh object.
        face_index: Index of the face to extract (default: 0).

    Returns:
        list: [[x,y,z], [x,y,z], [x,y,z], [x,y,z]] — 4 vertices in world space.
    """
    # TODO: Implement
    # Steps:
    #   1. Get evaluated mesh: depsgraph = context.evaluated_depsgraph_get()
    #   2. eval_obj = obj.evaluated_get(depsgraph)
    #   3. mesh_data = eval_obj.to_mesh()
    #   4. face = mesh_data.polygons[face_index]
    #   5. verts = [obj.matrix_world @ mesh_data.vertices[vi].co for vi in face.vertices]
    #   6. eval_obj.to_mesh_clear()
    #   7. return [[v.x, v.y, v.z] for v in verts]
    pass
