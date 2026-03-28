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

        layout.label(text="Case Settings")
        layout.prop(scene_props, "case_path")
        layout.prop(scene_props, "bashrc_path")

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
                layout.label(text="Grading")
                layout.prop(props, "grading_type")
                if props.grading_type == "RATIO":
                    layout.prop(props, "grading")
                elif props.grading_type == "START_SIZE":
                    layout.prop(props, "start_size")
                elif props.grading_type == "SYMMETRIC":
                    layout.prop(props, "start_size")
                    layout.prop(props, "end_size")

                # --- STL Projection controls ---
                if props.block_type == "box":
                    layout.separator()
                    layout.label(text="STL Projection (optional)")
                    layout.prop(props, "stl_projection_face")
                    layout.prop(props, "stl_file")

        # --- Auto-Update Mesh controls ---
        layout.separator()
        layout.label(text="Auto-Update Mesh")
        layout.prop(scene_props, "use_auto_update")
        if scene_props.use_auto_update:
            layout.prop(scene_props, "auto_update_limit")
            layout.prop(scene_props, "auto_update_delay")

        # --- Mesh quality display ---
        quality = context.scene.get("classy_last_mesh_quality")
        if quality:
            layout.separator()
            layout.label(text=f"Last Quality: {quality}", icon='CHECKMARK')

        layout.separator()
        layout.operator("classy.generate_mesh", text="1. Generate blockMeshDict")
        layout.operator("classy.run_blockmesh", text="2. Run blockMesh")
        layout.operator("classy.convert_vtk", text="3. Convert to VTK")
        layout.operator("classy.reload_mesh", text="4. Reload in Blender")
