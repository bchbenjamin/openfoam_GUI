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
        if obj and obj.type == 'MESH':
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
                row.prop(props, "force_include", text="Force Include (Ignore zero-thickness)")
                if props.force_include:
                    warn_row = header_box.row()
                    warn_row.alert = True
                    warn_row.label(text="⚠ May cause blockMesh crash if actually 2D", icon='ERROR')
                # Unapplied transform warning
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

                # --- Block-type specific parameters ---
                if props.block_type == "EXTRUDE":
                    ext_box = layout.box()
                    ext_box.label(text="Extrude Parameters")
                    ext_box.prop(props, "extrude_face_index")
                    ext_box.prop(props, "extrude_axis")
                    ext_box.prop(props, "extrude_distance")

                elif props.block_type == "REVOLVE":
                    rev_box = layout.box()
                    rev_box.label(text="Revolve Parameters")
                    rev_box.prop(props, "revolve_face_index")
                    rev_box.prop(props, "revolve_angle")
                    rev_box.prop(props, "revolve_axis")
                    rev_box.prop(props, "revolve_origin")

                elif props.block_type == "BOX":
                    # STL projection (terrain) — only for BOX type
                    stl_box = layout.box()
                    stl_box.label(text="STL Face Projection (optional — terrain only)")
                    stl_box.prop(props, "stl_projection_face")
                    stl_box.prop(props, "stl_file")

                elif props.block_type == "LOFT":
                    loft_box = layout.box()
                    loft_box.label(text="Loft Parameters", icon='MOD_SOLIDIFY')
                    loft_box.prop(props, "loft_bottom_face_index")
                    loft_box.prop(props, "loft_top_face_index")

                elif props.block_type == "WEDGE":
                    wedge_box = layout.box()
                    wedge_box.label(text="Wedge Parameters (Axisymmetric)", icon='MOD_SCREW')
                    wedge_box.prop(props, "wedge_face_index")
                    wedge_box.prop(props, "wedge_angle")

                # --- Shape Chaining controls ---
                if props.block_type in ("BOX", "EXTRUDE", "REVOLVE", "LOFT", "WEDGE"):
                    # Chaining only makes sense for cylinder/frustum sources,
                    # but any block can declare a chain_source
                    pass  # No chaining UI for non-round block types

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
