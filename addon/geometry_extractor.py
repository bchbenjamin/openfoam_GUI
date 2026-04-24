"""
addon/geometry_extractor.py
Extracts geometry from Blender objects and converts them into
a spec dict that mesh_builder.build_from_spec() can consume.

UNIVERSAL APPROACH:
  Every mesh object is treated identically:
    1. Extract its world-space bounding box → cb.Box(p_min, p_max)
    2. Flag it for STL self-projection (all 6 faces projected onto the
       object's own exported STL surface)

  This means:
    - A cylinder's bounding box deforms into a cylinder via projection
    - A sphere's bounding box deforms into a sphere
    - A monkey head's bounding box deforms into a monkey shape
    - A plain cube stays a cube (projection onto itself = no change)

  No shape auto-detection needed. One pipeline for all geometry.

REQUIRES BLENDER PYTHON (bpy) — cannot be run standalone.

CALLED BY: operators.py → CLASSY_OT_generate_mesh.execute()
"""

import bpy
from mathutils import Vector


def extract_geometry(context):
    """
    Scans all mesh objects in the current Blender scene and extracts
    their geometry into a spec dict for mesh_builder.build_from_spec().

    Every mesh object is automatically included unless explicitly excluded
    via the exclude_from_mesh toggle.
    """
    blocks = []

    for obj in context.scene.objects:
        # Skip non-mesh objects
        if obj.type != 'MESH':
            print(f"[classy_blocks] Skipping non-mesh: '{obj.name}' (type={obj.type})")
            continue

        props = getattr(obj, "classy_block_props", None)

        # Check exclusion toggle
        if props and getattr(props, "exclude_from_mesh", False):
            print(f"[classy_blocks] Skipping excluded: '{obj.name}'")
            continue

        # Read cells with safe access
        raw_cells = getattr(props, "cells", None) if props else None
        if raw_cells is not None and len(raw_cells) >= 3:
            cells = [max(1, int(raw_cells[i])) for i in range(3)]
        else:
            cells = [10, 10, 10]

        # Read grading with safe access
        raw_grading = getattr(props, "grading", None) if props else None
        if raw_grading is not None and len(raw_grading) >= 3:
            grading = [float(raw_grading[i]) for i in range(3)]
        else:
            grading = [1.0, 1.0, 1.0]

        patch_name = getattr(props, "patch_name", "defaultWall") if props else "defaultWall"
        patch_name = patch_name or "defaultWall"

        grading_type = getattr(props, "grading_type", "RATIO") if props else "RATIO"
        start_size = getattr(props, "start_size", 1e-4) if props else 1e-4
        end_size = getattr(props, "end_size", 1e-4) if props else 1e-4

        try:
            block_spec = _extract_universal(obj, cells, grading, patch_name,
                                            grading_type, start_size, end_size)
            blocks.append(block_spec)
            print(f"[classy_blocks] Extracted block: '{obj.name}' "
                  f"p_min={[round(v,4) for v in block_spec['p_min']]}, "
                  f"p_max={[round(v,4) for v in block_spec['p_max']]}, "
                  f"needs_projection={block_spec['needs_self_projection']}")

        except Exception as e:
            print(f"[classy_blocks] ERROR extracting '{obj.name}': {e}")
            import traceback; traceback.print_exc()
            continue

    print(f"[classy_blocks] Total blocks extracted: {len(blocks)}")
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
    """
    world_coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    p_min = [min(co[i] for co in world_coords) for i in range(3)]
    p_max = [max(co[i] for co in world_coords) for i in range(3)]

    return (p_min, p_max)


def _is_box_shaped(obj):
    """
    Returns True if the object is a simple axis-aligned box (cube/cuboid).
    A box has exactly 8 vertices and 6 quad faces.
    If True, we skip STL self-projection since Box already matches exactly.
    """
    mesh_data = obj.data
    verts = len(mesh_data.vertices)
    faces = len(mesh_data.polygons)

    # Standard Blender cube: 8 verts, 6 faces, all quads
    if verts == 8 and faces == 6:
        all_quads = all(len(f.vertices) == 4 for f in mesh_data.polygons)
        if all_quads:
            print(f"[classy_blocks]   '{obj.name}' is a plain box (8v/6f) — skipping self-projection")
            return True

    return False


def _extract_universal(obj, cells, grading, patch_name,
                       grading_type="RATIO", start_size=1e-4, end_size=1e-4):
    """
    Universal extractor: creates a box block spec from any mesh object.

    For non-box shapes (cylinders, spheres, monkey heads, etc.), the spec
    includes needs_self_projection=True. The operator will export the
    object as an STL and project all 6 box faces onto it, making the
    structured hex mesh conform to the actual shape.

    For plain cubes/boxes (8 verts, 6 quad faces), self-projection is
    skipped since the bounding box already matches exactly.
    """
    p_min, p_max = _get_world_bounding_box(obj)

    # Determine if this object needs self-projection
    needs_projection = not _is_box_shaped(obj)

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
        "needs_self_projection": needs_projection,
    }

    # Also check for user-specified STL projection (from the UI)
    props = getattr(obj, "classy_block_props", None)
    if props:
        stl_file = getattr(props, "stl_file", "") or ""
        if stl_file:
            import os
            stl_face = getattr(props, "stl_projection_face", "top")
            spec["stl_projections"] = {
                stl_face: os.path.basename(stl_file)
            }

    return spec
