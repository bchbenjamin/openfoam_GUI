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

        layout.separator()
        layout.operator("classy.generate_mesh", text="1. Generate blockMeshDict")
        layout.operator("classy.run_blockmesh", text="2. Run blockMesh")
        layout.operator("classy.convert_vtk", text="3. Convert to VTK")
        layout.operator("classy.reload_mesh", text="4. Reload in Blender")
