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
        obj = context.active_object

        # --- Pipeline Status Header ---
        if scene_props.pipeline_status != "Ready":
            layout.label(text=scene_props.pipeline_status, icon='INFO')
            layout.separator()

        layout.label(text="Case Settings")
        layout.prop(scene_props, "case_path")

        if obj:
            layout.separator()
            props = obj.classy_block_props
            layout.prop(props, "is_block", text=f"Tag '{obj.name}' as Block")
            if props.is_block:
                layout.prop(props, "block_type")
                layout.prop(props, "cells")
                layout.prop(props, "patch_name")

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

                # --- STL Projection controls ---
                if props.block_type == "box":
                    layout.separator()
                    box_stl = layout.box()
                    box_stl.label(text="STL Projection (optional)")
                    box_stl.prop(props, "stl_projection_face")
                    box_stl.prop(props, "stl_file")

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
            blocks_count = sum(1 for o in context.scene.objects if getattr(o, "classy_block_props", None) and o.classy_block_props.is_block)
            if blocks_count > prefs.auto_update_limit:
                layout.label(text=f"Disabled: Project too large (> {prefs.auto_update_limit} blocks)", icon='ERROR')

        # --- Mesh quality display ---
        quality = scene_props.last_mesh_quality
        if quality:
            layout.separator()
            layout.label(text=f"Last Quality: {quality}", icon=scene_props.last_mesh_quality_icon)

        layout.separator()
        layout.operator("classy.generate_mesh", text="1. Generate blockMeshDict")
        layout.operator("classy.run_blockmesh", text="2. Run blockMesh")
        layout.operator("classy.convert_vtk", text="3. Convert to VTK")
        layout.operator("classy.reload_mesh", text="4. Reload in Blender")
