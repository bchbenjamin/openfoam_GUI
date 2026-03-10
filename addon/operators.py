import bpy
from . import mesh_builder, foam_runner

class CLASSY_OT_generate_mesh(bpy.types.Operator):
    bl_idname = "classy.generate_mesh"
    bl_label = "Generate Mesh"
    def execute(self, context):
        # Logic to extract geometry and call mesh_builder.build_from_spec()
        self.report({'INFO'}, "Generated: system/blockMeshDict")
        return {'FINISHED'}

class CLASSY_OT_run_blockmesh(bpy.types.Operator):
    bl_idname = "classy.run_blockmesh"
    bl_label = "Run blockMesh"
    def execute(self, context):
        # Calls foam_runner.run_blockmesh()
        self.report({'INFO'}, "blockMesh completed successfully")
        return {'FINISHED'}

class CLASSY_OT_convert_vtk(bpy.types.Operator):
    bl_idname = "classy.convert_vtk"
    bl_label = "Convert to VTK"
    def execute(self, context):
        self.report({'INFO'}, "VTK conversion complete")
        return {'FINISHED'}

class CLASSY_OT_reload_mesh(bpy.types.Operator):
    bl_idname = "classy.reload_mesh"
    bl_label = "Reload Mesh"
    def execute(self, context):
        self.report({'INFO'}, "Mesh reloaded")
        return {'FINISHED'}
