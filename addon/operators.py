import os
import bpy
from . import mesh_builder, foam_runner, geometry_extractor, vtk_importer


class CLASSY_OT_generate_mesh(bpy.types.Operator):
    """Generate blockMeshDict from tagged Blender objects"""
    bl_idname = "classy.generate_mesh"
    bl_label = "Generate Mesh"

    def execute(self, context):
        scene_props = context.scene.classy_mesh_props
        case_path = scene_props.case_path

        # Path validation guard
        if not case_path:
            self.report({'ERROR'},
                        "Case directory is not set — open the Classy Blocks "
                        "panel and set the Case Directory field")
            return {'CANCELLED'}

        case_path = os.path.expanduser(case_path)
        output_path = os.path.join(case_path, "system", "blockMeshDict")

        try:
            # Extract geometry from tagged Blender objects
            spec = geometry_extractor.extract_geometry(context)

            if not spec["blocks"]:
                self.report({'ERROR'},
                            "No block objects found — tag at least one "
                            "object as a block in the Classy Blocks panel")
                return {'CANCELLED'}

            # Ensure the system/ directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Build the blockMeshDict
            mesh_builder.build_from_spec(spec, output_path)

            file_size = os.path.getsize(output_path)
            self.report({'INFO'},
                        f"Generated: {output_path} ({file_size} bytes)")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'},
                        f"blockMeshDict generation failed: {str(e)}")
            return {'CANCELLED'}


class CLASSY_OT_run_blockmesh(bpy.types.Operator):
    """Run OpenFOAM blockMesh on the current case"""
    bl_idname = "classy.run_blockmesh"
    bl_label = "Run blockMesh"

    def execute(self, context):
        scene_props = context.scene.classy_mesh_props
        case_path = scene_props.case_path
        bashrc_path = scene_props.bashrc_path

        # Path validation guard
        if not case_path:
            self.report({'ERROR'},
                        "Case directory is not set — open the Classy Blocks "
                        "panel and set the Case Directory field")
            return {'CANCELLED'}

        case_path = os.path.expanduser(case_path)

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
                if non_ortho is not None:
                    quality_str += f"Non-orthogonality: {non_ortho:.1f}"
                if skewness is not None:
                    quality_str += f" | Skewness: {skewness:.2f}"

                if quality_str:
                    self.report({'INFO'},
                                f"blockMesh completed — {quality_str}")
                else:
                    self.report({'INFO'},
                                "blockMesh completed successfully")
                return {'FINISHED'}
            else:
                # Report truncated stderr on failure
                err_msg = stderr[:500] if stderr else "No error output"
                self.report({'ERROR'},
                            f"blockMesh failed (exit code {returncode}): "
                            f"{err_msg}")
                return {'CANCELLED'}

        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'},
                        f"blockMesh execution failed: {str(e)}")
            return {'CANCELLED'}


class CLASSY_OT_convert_vtk(bpy.types.Operator):
    """Run foamToVTK to convert OpenFOAM mesh to VTK format"""
    bl_idname = "classy.convert_vtk"
    bl_label = "Convert to VTK"

    def execute(self, context):
        scene_props = context.scene.classy_mesh_props
        case_path = scene_props.case_path
        bashrc_path = scene_props.bashrc_path

        # Path validation guard
        if not case_path:
            self.report({'ERROR'},
                        "Case directory is not set — open the Classy Blocks "
                        "panel and set the Case Directory field")
            return {'CANCELLED'}

        case_path = os.path.expanduser(case_path)

        # Check that blockMesh has been run first
        poly_mesh = os.path.join(case_path, "constant", "polyMesh")
        if not os.path.isdir(poly_mesh):
            self.report({'ERROR'},
                        f"polyMesh not found at {poly_mesh} — "
                        "run blockMesh first (button 2)")
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
                return {'FINISHED'}
            else:
                err_msg = stderr[:500] if stderr else "No error output"
                self.report({'ERROR'},
                            f"foamToVTK failed (exit code {returncode}): "
                            f"{err_msg}")
                return {'CANCELLED'}

        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'},
                        f"foamToVTK execution failed: {str(e)}")
            return {'CANCELLED'}


class CLASSY_OT_reload_mesh(bpy.types.Operator):
    """Reload the VTK mesh result into Blender"""
    bl_idname = "classy.reload_mesh"
    bl_label = "Reload Mesh"

    def execute(self, context):
        scene_props = context.scene.classy_mesh_props
        case_path = scene_props.case_path

        # Path validation guard
        if not case_path:
            self.report({'ERROR'},
                        "Case directory is not set — open the Classy Blocks "
                        "panel and set the Case Directory field")
            return {'CANCELLED'}

        case_path = os.path.expanduser(case_path)

        try:
            vtk_files = vtk_importer.find_vtk_files(case_path)

            if not vtk_files:
                self.report({'ERROR'},
                            f"No VTK files found in {case_path}/VTK/ — "
                            "run foamToVTK first (button 3)")
                return {'CANCELLED'}

            # Load the first VTK file found
            vtk_path = vtk_files[0]
            result = vtk_importer.load_vtk_as_blender_mesh(vtk_path)

            if result is None:
                self.report({'WARNING'},
                            "VTK importer returned None — check System "
                            "Console for details")
                return {'CANCELLED'}

            self.report({'INFO'},
                        f"Mesh reloaded from {os.path.basename(vtk_path)}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'},
                        f"Mesh reload failed: {str(e)}")
            return {'CANCELLED'}
