import os
import datetime
import bpy
from . import mesh_builder, foam_runner, geometry_extractor, vtk_importer, case_setup

def set_status(context, status_msg):
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    context.scene.classy_mesh_props.pipeline_status = f"[{time_str}] {status_msg}"
    if hasattr(context, "area") and context.area:
        context.area.tag_redraw()



class CLASSY_OT_generate_mesh(bpy.types.Operator):
    """Generate blockMeshDict from tagged Blender objects"""
    bl_idname = "classy.generate_mesh"
    bl_label = "Generate Mesh"

    def execute(self, context):
        set_status(context, "Generating blockMeshDict...")
        scene_props = context.scene.classy_mesh_props
        case_path = scene_props.case_path

        # Path validation guard
        if not case_path:
            self.report({'ERROR'},
                        "Case directory is not set — open the Classy Blocks "
                        "panel and set the Case Directory field")
            set_status(context, "Failed: Case directory not set")
            return {'CANCELLED'}

        case_path = os.path.expanduser(case_path)
        
        # Verify case directory exists (or at least its parent if we are generating)
        if not os.path.exists(os.path.dirname(case_path)):
            self.report({'ERROR'},
                        f"blockMeshDict generation failed: parent of case directory not found at "
                        f"'{case_path}' — check the Case Directory field")
            set_status(context, "Failed: Invalid case parent path")
            return {'CANCELLED'}

        output_path = os.path.join(case_path, "system", "blockMeshDict")

        try:
            # Extract geometry from tagged Blender objects
            spec = geometry_extractor.extract_geometry(context)

            if not spec["blocks"]:
                self.report({'ERROR'},
                            "No block objects found — tag at least one "
                            "object as a block in the Classy Blocks panel")
                set_status(context, "Failed: No blocks tagged")
                return {'CANCELLED'}

            # Ensure the system/ directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Build the blockMeshDict
            mesh_builder.build_from_spec(spec, output_path)

            # Setup the complete OpenFOAM case (controlDict, etc.)
            patch_names = list(set([b.get("patch_name", "defaultWall") for b in spec["blocks"]]))
            case_setup.setup_incompressible_case(case_path, patch_names)

            file_size = os.path.getsize(output_path)
            self.report({'INFO'},
                        f"Generated blockMeshDict ({file_size} bytes) & Case Files")
            set_status(context, "Success: blockMeshDict generated")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'},
                        f"blockMeshDict generation failed: {str(e)}")
            set_status(context, "Failed: check console")
            return {'CANCELLED'}


class CLASSY_OT_run_blockmesh(bpy.types.Operator):
    """Run OpenFOAM blockMesh on the current case"""
    bl_idname = "classy.run_blockmesh"
    bl_label = "Run blockMesh"

    def execute(self, context):
        set_status(context, "Running blockMesh...")
        scene_props = context.scene.classy_mesh_props
        case_path = scene_props.case_path
        bashrc_path = context.preferences.addons[__package__].preferences.bashrc_path

        # Path validation guard
        if not case_path:
            self.report({'ERROR'},
                        "Case directory is not set — open the Classy Blocks "
                        "panel and set the Case Directory field")
            set_status(context, "Failed: Case directory not set")
            return {'CANCELLED'}

        case_path = os.path.expanduser(case_path)

        if not os.path.isdir(case_path):
            self.report({'ERROR'},
                        f"blockMesh failed: case directory not found at "
                        f"'{case_path}' — check the Case Directory field")
            set_status(context, "Failed: Case directory not found")
            return {'CANCELLED'}

        try:
            returncode, stdout, stderr = foam_runner.run_blockmesh(
                case_path, bashrc_path
            )

            if returncode == 0:
                # Parse mesh quality from the combined output
                combined_output = stdout + stderr
                quality = foam_runner.parse_mesh_quality(combined_output)

                non_ortho = quality.get("non_orthogonality")
                skewness = quality.get("skewness")

                quality_str = ""
                icon = 'CHECKMARK'
                
                if non_ortho is not None:
                    quality_str += f"Non-ortho: {non_ortho:.1f}"
                    if non_ortho > 70:
                        icon = 'ERROR'
                    elif non_ortho > 60 and icon != 'ERROR':
                        icon = 'QUESTION'
                        
                if skewness is not None:
                    quality_str += f" | Skewness: {skewness:.2f}"
                    if skewness > 4.0:
                        icon = 'ERROR'
                    elif skewness > 2.0 and icon != 'ERROR':
                        icon = 'QUESTION'

                if quality_str:
                    scene_props.last_mesh_quality = quality_str
                    scene_props.last_mesh_quality_icon = icon
                    self.report({'INFO'}, f"blockMesh completed — {quality_str}")
                else:
                    scene_props.last_mesh_quality = "OK"
                    scene_props.last_mesh_quality_icon = 'CHECKMARK'
                    self.report({'INFO'}, "blockMesh completed successfully")
                    
                set_status(context, "Success: blockMesh completed")
                return {'FINISHED'}
            else:
                # Report truncated stderr on failure
                err_msg = stderr[:500] if stderr else "No error output"
                self.report({'ERROR'},
                            f"blockMesh failed (exit code {returncode}): "
                            f"{err_msg}")
                set_status(context, "Failed: blockMesh error")
                return {'CANCELLED'}

        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
            set_status(context, "Failed: FileNotFound error")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'},
                        f"blockMesh execution failed: {str(e)}")
            set_status(context, "Failed: Exception occurred")
            return {'CANCELLED'}


class CLASSY_OT_convert_vtk(bpy.types.Operator):
    """Run foamToVTK to convert OpenFOAM mesh to VTK format"""
    bl_idname = "classy.convert_vtk"
    bl_label = "Convert to VTK"

    def execute(self, context):
        set_status(context, "Running foamToVTK...")
        scene_props = context.scene.classy_mesh_props
        case_path = scene_props.case_path
        bashrc_path = context.preferences.addons[__package__].preferences.bashrc_path

        # Path validation guard
        if not case_path:
            self.report({'ERROR'},
                        "Case directory is not set — open the Classy Blocks "
                        "panel and set the Case Directory field")
            set_status(context, "Failed: Case directory not set")
            return {'CANCELLED'}

        case_path = os.path.expanduser(case_path)

        if not os.path.isdir(case_path):
            self.report({'ERROR'},
                        f"foamToVTK failed: case directory not found at "
                        f"'{case_path}' — check the Case Directory field")
            set_status(context, "Failed: Case directory not found")
            return {'CANCELLED'}

        # Check that blockMesh has been run first
        poly_mesh = os.path.join(case_path, "constant", "polyMesh")
        if not os.path.isdir(poly_mesh):
            self.report({'ERROR'},
                        f"polyMesh not found at {poly_mesh} — "
                        "run blockMesh first (button 2)")
            set_status(context, "Failed: polyMesh not found")
            return {'CANCELLED'}

        try:
            returncode, stdout, stderr = foam_runner.run_foam_to_vtk(
                case_path, bashrc_path
            )

            if returncode == 0:
                # Count VTK files produced
                vtk_files = vtk_importer.find_vtk_files(case_path)
                self.report({'INFO'},
                            f"VTK conversion complete — "
                            f"{len(vtk_files)} file(s) created")
                set_status(context, "Success: VTK conversion complete")
                return {'FINISHED'}
            else:
                err_msg = stderr[:500] if stderr else "No error output"
                self.report({'ERROR'},
                            f"foamToVTK failed (exit code {returncode}): "
                            f"{err_msg}")
                set_status(context, "Failed: foamToVTK output error")
                return {'CANCELLED'}

        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
            set_status(context, "Failed: FileNotFoundError")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'},
                        f"foamToVTK execution failed: {str(e)}")
            set_status(context, "Failed: foamToVTK exception")
            return {'CANCELLED'}


class CLASSY_OT_reload_mesh(bpy.types.Operator):
    """Reload the VTK mesh result into Blender"""
    bl_idname = "classy.reload_mesh"
    bl_label = "Reload Mesh"

    def execute(self, context):
        set_status(context, "Reloading VTK Mesh...")
        scene_props = context.scene.classy_mesh_props
        case_path = scene_props.case_path

        # Path validation guard
        if not case_path:
            self.report({'ERROR'},
                        "Case directory is not set — open the Classy Blocks "
                        "panel and set the Case Directory field")
            set_status(context, "Failed: Case directory not set")
            return {'CANCELLED'}

        case_path = os.path.expanduser(case_path)

        if not os.path.isdir(case_path):
            self.report({'ERROR'},
                        f"Mesh reload failed: case directory not found at "
                        f"'{case_path}' — check the Case Directory field")
            set_status(context, "Failed: Case directory not found")
            return {'CANCELLED'}

        try:
            vtk_files = vtk_importer.find_vtk_files(case_path)

            if not vtk_files:
                self.report({'ERROR'},
                            f"No VTK files found in {case_path}/VTK/ — "
                            "run foamToVTK first (button 3)")
                set_status(context, "Failed: No VTK files")
                return {'CANCELLED'}

            # Load the first VTK file found
            vtk_path = vtk_files[0]
            result = vtk_importer.load_vtk_as_blender_mesh(vtk_path)

            if result is None:
                self.report({'WARNING'},
                            "VTK importer returned None — check System "
                            "Console for details")
                set_status(context, "Failed: VTK importer error")
                return {'CANCELLED'}

            self.report({'INFO'},
                        f"Mesh reloaded from {os.path.basename(vtk_path)}")
            set_status(context, "Success: Mesh reloaded")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'},
                        f"Mesh reload failed: {str(e)}")
            set_status(context, "Failed: Reload exception")
            return {'CANCELLED'}

class MESH_OT_export_terrain_stl(bpy.types.Operator):
    """(Week 7 feature placeholder) Export selected mesh as STL for terrain projection"""
    bl_idname = "mesh.classy_export_terrain"
    bl_label = "Export as Terrain STL"

    def execute(self, context):
        self.report({'INFO'}, "Terrain export will be implemented in Week 7!")
        return {'FINISHED'}
