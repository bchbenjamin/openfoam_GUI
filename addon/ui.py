"""
User Interface for the Classy Blocks add-on.

Provides the 3D Viewport side-panel (N-panel) UI, enabling users to interact with
the Parametric Structured Mesh Builder, set boundary conditions, and run pipelines.
"""

# pyrefly: ignore [missing-import]
import bpy

class CLASSY_PT_main_panel(bpy.types.Panel):
    bl_label = "Classy Blocks Mesh"
    bl_idname = "CLASSY_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ClasyMesh'

    def draw(self, context):
        layout = self.layout
        scene_props = context.scene.classy_mesh_props

        from . import dependencies
        
        # --- Python Dependencies Check ---
        if not dependencies.check_python_deps():
            box = layout.box()
            box.label(text="Missing Python Packages", icon='ERROR')
            box.label(text="classy_blocks and pyvista are required.")
            box.operator("classy.install_python_deps", icon='IMPORT')
            return  # Hide the rest of the UI until installed

        # --- OpenFOAM Check ---
        if not dependencies.get_openfoam_status(context):
            of_box = layout.box()
            of_box.label(text="OpenFOAM Not Found", icon='ERROR')
            of_box.label(text="Meshing requires OpenFOAM to be installed.")
            of_box.operator("classy.install_openfoam", icon='CONSOLE')
            layout.separator()

        # --- Pipeline Status Header ---
        if scene_props.pipeline_status != "Ready":
            layout.label(text=scene_props.pipeline_status, icon='INFO')
            layout.separator()

        if scene_props.structure_warning:
            warning_box = layout.box()
            for index, line in enumerate(scene_props.structure_warning.split(" | ")):
                warning_box.label(
                    text=line,
                    icon='ERROR' if index == 0 else 'BLANK1'
                )
            layout.separator()

        if context.mode == 'OBJECT':
            add_box = layout.box()
            add_box.label(text="Add Classy Primitives", icon='MESH_DATA')
            row = add_box.row()
            row.operator("classy.add_box", text="Box", icon='MESH_CUBE')
            row.operator("classy.add_cylinder", text="Cylinder", icon='MESH_CYLINDER')
            row.operator("classy.add_frustum", text="Frustum", icon='MESH_CONE')
            
            row2 = add_box.row()
            row2.operator("classy.add_sketch_point", text="Draw Sketch", icon='GREASEPENCIL')
            
            layout.separator()

        layout.label(text="Case Settings")
        layout.prop(scene_props, "case_path")

        # --- Scene-wide block count summary ---
        mesh_objects = [o for o in context.scene.objects if o.type == 'MESH']
        excluded = sum(1 for o in mesh_objects
                       if getattr(o, "classy_block_props", None)
                       and o.classy_block_props.exclude_from_mesh)
        active_blocks = len(mesh_objects) - excluded
        layout.label(text=f"Mesh Objects: {active_blocks} blocks "
                     f"({excluded} excluded)", icon='MESH_CUBE')

        # --- Per-object settings (shown for active selection) ---
        obj = context.active_object
        if obj and obj.type == 'CURVE' and obj.get("classy_sketch"):
            layout.separator()
            sketch_box = layout.box()
            sketch_box.label(text="Sketch Actions", icon='CURVE_PATH')
            
            curve = obj.data
            num_pts = 0
            if curve.splines:
                spline = curve.splines[0]
                num_pts = len(spline.bezier_points) if spline.type == 'BEZIER' else len(spline.points)
            
            if num_pts == 4:
                sketch_box.label(text="Valid 4-Point Profile", icon='CHECKMARK')
            else:
                warn_row = sketch_box.row()
                warn_row.alert = True
                warn_row.label(
                    text=f"⚠ Invalid Profile: Sketch has {num_pts} points. Exactly 4 points required.",
                    icon='ERROR'
                )
            
            row = sketch_box.row()
            row.operator("classy.extrude_sketch")
            row.operator("classy.revolve_sketch")

        if obj and (obj.type == 'MESH' or (obj.type == 'CURVE' and obj.get("classy_sketch"))):
            layout.separator()
            
            if context.mode == 'EDIT_MESH':
                edit_box = layout.box()
                edit_box.label(text="2D Sketch Tools", icon='EDITMODE_HLT')
                edit_box.operator("classy.tag_extrude")
                edit_box.operator("classy.tag_revolve")
                edit_box.operator("classy.tag_loft")
                layout.separator()
                
            props = obj.classy_block_props

            # Exclusion toggle
            header_box = layout.box()
            row = header_box.row()
            icon = 'CANCEL' if props.exclude_from_mesh else 'CHECKMARK'
            row.prop(props, "exclude_from_mesh",
                     text=f"Exclude '{obj.name}'", icon=icon)

            if not props.exclude_from_mesh:
                row = header_box.row()
                
                # Unapplied transform warning (deprecated in Phase 1, handled in geometry_extractor, but UI check is nice)
                scale = obj.scale
                if (abs(scale[0] - 1.0) > 1e-4 or
                    abs(scale[1] - 1.0) > 1e-4 or
                    abs(scale[2] - 1.0) > 1e-4):
                    warn_row = header_box.row()
                    warn_row.alert = True
                    warn_row.label(
                        text="⚠ Unapplied Scale — Ctrl+A to apply",
                        icon='ERROR'
                    )

                # Common settings
                header_box.prop(props, "cells")
                header_box.prop(props, "patch_name")
                header_box.prop(props, "block_type")

                if props.block_type == "EXTRUDED_RING":
                    ring_box = layout.box()
                    ring_box.label(text="Extruded Ring Parameters")
                    # (To be added: inner radius property in properties.py if needed, 
                    # but for now, rely on local space if they modeled a ring, or 
                    # we will add a property if needed. For now, empty or basic label)
                    ring_box.label(text="Extracted from Local Bounding Box", icon='INFO')

                elif props.block_type == "WEDGE":
                    wedge_box = layout.box()
                    wedge_box.label(text="Wedge Parameters (Axisymmetric)", icon='MOD_SCREW')
                    wedge_box.prop(props, "wedge_face_index")
                    wedge_box.prop(props, "wedge_angle")
                
                elif props.block_type == "EXTRUDE":
                    extrude_box = layout.box()
                    extrude_box.label(text="Extrude Parameters (Preview Mode)", icon='MESH_CUBE')
                    extrude_box.prop(props, "extrude_face_index")
                    extrude_box.prop(props, "extrude_axis")
                    extrude_box.prop(props, "extrude_distance")
                    if obj.type == 'CURVE':
                        extrude_box.label(text="* Visual preview only. Export to see OpenFOAM mesh.", icon='INFO')
                
                elif props.block_type == "REVOLVE":
                    revolve_box = layout.box()
                    revolve_box.label(text="Revolve Parameters (Preview Mode)", icon='MESH_CIRCLE')
                    revolve_box.prop(props, "revolve_face_index")
                    revolve_box.prop(props, "revolve_angle")
                    revolve_box.prop(props, "revolve_axis")
                    revolve_box.prop(props, "revolve_origin")
                    if obj.type == 'CURVE':
                        revolve_box.label(text="* Visual preview only. Export to see OpenFOAM mesh.", icon='INFO')
                    
                elif props.block_type == "LOFT":
                    loft_box = layout.box()
                    loft_box.label(text="Loft Parameters", icon='SURFACE_NSURFACE')
                    loft_box.prop(props, "loft_bottom_face_index")
                    loft_box.prop(props, "loft_top_face_index")

                # --- Shape Chaining controls ---
                if props.block_type in ("CYLINDER", "FRUSTUM"):
                    chain_box = layout.box()
                    chain_box.label(text="Shape Chaining (Pipe Networks)", icon='LINKED')
                    chain_box.prop_search(
                        props, "chain_source",
                        context.scene, "objects",
                        text="Chain From"
                    )
                    if props.chain_source:
                        chain_box.prop(props, "chain_length")
                        chain_box.prop(props, "chain_radius_2")

                # --- STL Projection (Terrain) ---
                layout.separator()
                stl_box = layout.box()
                stl_box.label(text="STL Face Projection (Terrain Mapping)", icon='MOD_SHRINKWRAP')
                stl_box.prop(props, "stl_projection_face")
                stl_box.prop(props, "stl_projection_direction")
                stl_box.prop(props, "stl_file")
                if props.stl_file:
                    stl_box.operator("classy.project_to_stl", text="Validate STL", icon='CHECKMARK')

                # --- Boundary Conditions ---
                layout.separator()
                bc_box = layout.box()
                bc_box.label(text="Boundary Conditions", icon='MATERIAL')
                
                if props.block_type == "BOX":
                    sides = "left, right, front, back, bottom, top"
                elif props.block_type in ("CYLINDER", "FRUSTUM", "EXTRUDED_RING"):
                    sides = "bottom, top, outer, inner"
                else:
                    sides = "bottom, top, (lateral edges)"
                bc_box.label(text=f"Valid Sides: {sides}", icon='INFO')
                
                for idx, patch in enumerate(props.face_patches):
                    row = bc_box.row()
                    if idx == props.active_face_patch_index:
                        row.alert = True
                    row.prop(patch, "side_name", text="")
                    row.prop(patch, "patch_name", text="")
                    row.prop(patch, "patch_type", text="")
                
                row = bc_box.row()
                row.operator("classy.add_boundary_patch", icon='ADD')
                row.operator("classy.remove_boundary_patch", icon='REMOVE')
                row.prop(props, "active_face_patch_index", text="Selected")

                # --- Grading controls ---
                layout.separator()
                box = layout.box()
                box.label(text="Grading")
                box.prop(props, "grading_type")
                if props.grading_type == "RATIO":
                    box.prop(props, "grading")
                elif props.grading_type == "START_SIZE":
                    box.prop(props, "start_size")
                elif props.grading_type == "SYMMETRIC":
                    box.prop(props, "start_size")
                    box.prop(props, "end_size")

        # --- STL Export Section ---
        layout.separator()
        layout.label(text="Terrain Utilities")
        col = layout.column()
        col.enabled = bool(obj and obj.select_get())
        col.operator("mesh.classy_export_terrain", text="Export as Terrain STL")

        # --- Auto-Update Mesh controls ---
        layout.separator()
        layout.label(text="Auto-Update Mesh")
        layout.prop(scene_props, "use_auto_update")

        if scene_props.use_auto_update:
            prefs = context.preferences.addons[__package__].preferences
            if active_blocks > prefs.auto_update_limit:
                layout.label(
                    text=f"Disabled: Project too large "
                         f"(> {prefs.auto_update_limit} blocks)",
                    icon='ERROR')

        # --- Mesh quality display ---
        quality = scene_props.last_mesh_quality
        if quality:
            layout.separator()
            layout.label(text=f"Last Quality: {quality}",
                         icon=scene_props.last_mesh_quality_icon)

        # --- Primary action: full pipeline in one click ---
        layout.separator()
        run_all_row = layout.row()
        run_all_row.scale_y = 1.5
        run_all_row.operator("classy.run_all", text="▶ Run All", icon='PLAY')

        # --- Individual pipeline steps (for debugging / partial runs) ---
        layout.separator()
        layout.operator("classy.generate_mesh", text="1. Generate blockMeshDict")
        layout.operator("classy.run_blockmesh", text="2. Run blockMesh")
        layout.operator("classy.convert_vtk", text="3. Convert to VTK")
        layout.operator("classy.reload_mesh", text="4. Reload in Blender")
