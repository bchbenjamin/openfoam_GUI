import os
import datetime
import bpy
from . import mesh_builder, foam_runner, geometry_extractor, vtk_importer, case_setup
from . import foam_path_utils

def set_status(context, status_msg):
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    context.scene.classy_mesh_props.pipeline_status = f"[{time_str}] {status_msg}"
    if hasattr(context, "area") and context.area:
        context.area.tag_redraw()





def get_case_path(context):
    scene_props = context.scene.classy_mesh_props
    case_path = scene_props.case_path
    if not case_path:
        prefs = getattr(context.preferences.addons.get(__package__), "preferences", None)
        if prefs:
            case_path = prefs.default_case_dir
    return case_path

class CLASSY_OT_generate_mesh(bpy.types.Operator):
    """Generate blockMeshDict from tagged Blender objects"""
    bl_idname = "classy.generate_mesh"
    bl_label = "Generate Mesh"

    def execute(self, context):
        set_status(context, "Generating blockMeshDict...")
        scene_props = context.scene.classy_mesh_props
        scene_props.structure_warning = ""
        case_path = get_case_path(context)

        if not case_path:
            def draw_error(self, context):
                self.layout.label(text="Case directory is not set!", icon='ERROR')
                self.layout.label(text="Open the Classy Blocks panel and set the Case Directory.")
            context.window_manager.popup_menu(draw_error, title="No Case Directory", icon='ERROR')
            self.report({'ERROR'}, "Case directory is not set")
            set_status(context, "Failed: Case directory not set")
            return {'CANCELLED'}

        case_path = foam_path_utils.resolve_case_path(case_path)

        # Validate against FOAM_RUN environment context
        foam_run = ""
        if hasattr(context.scene, "foam_dirs"):
            foam_run = context.scene.foam_dirs.foam_run_dir
        validation = foam_path_utils.validate_case_path(case_path, foam_run)
        for warning in validation["warnings"]:
            self.report({'WARNING'}, warning)

        output_path = os.path.join(case_path, "system", "blockMeshDict")

        # Create the full directory tree (case + system/) if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            spec = geometry_extractor.extract_geometry(context)
            meshable_blocks = [
                block for block in spec["blocks"]
                if block.get("type") != "unsupported"
            ]


            warnings = spec.get("warnings", [])
            if warnings:
                warning_msg = "Unsupported objects will be skipped: " + " | ".join(
                    warning.split(": ", 1)[0] for warning in warnings[:4]
                )
                if len(warnings) > 4:
                    warning_msg += f" | +{len(warnings) - 4} more"
                scene_props.structure_warning = warning_msg
                self.report({'WARNING'}, warning_msg)

            if not spec["blocks"]:
                self.report({'ERROR'},
                            "No mesh objects found — add at least one mesh object")
                set_status(context, "Failed: No mesh objects")
                return {'CANCELLED'}

            if not meshable_blocks:
                self.report({'ERROR'},
                            "No supported structured mesh objects found — "
                            "unsupported meshes were skipped")
                set_status(context, "Failed: No supported mesh objects")
                return {'CANCELLED'}

            # Build the blockMeshDict (auto-detection already classified shapes)
            mesh_builder.build_from_spec(spec, output_path)

            # Setup the complete OpenFOAM case (controlDict, etc.)
            patch_names = list(set(
                b.get("patch_name", "defaultWall") for b in meshable_blocks
            ))
            case_setup.setup_incompressible_case(case_path, patch_names)

            file_size = os.path.getsize(output_path)
            self.report({'INFO'},
                        f"Generated blockMeshDict ({file_size} bytes) & Case Files")
            set_status(context, "Success: blockMeshDict generated")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'},
                        f"blockMeshDict generation failed: {str(e)}")
            set_status(context, "Failed: check System Console")
            import traceback; traceback.print_exc()
            return {'CANCELLED'}


class CLASSY_OT_run_blockmesh(bpy.types.Operator):
    """Run OpenFOAM blockMesh on the current case"""
    bl_idname = "classy.run_blockmesh"
    bl_label = "Run blockMesh"

    def execute(self, context):
        set_status(context, "Running blockMesh...")
        scene_props = context.scene.classy_mesh_props
        case_path = get_case_path(context)
        bashrc_path = context.preferences.addons[__package__].preferences.bashrc_path

        # Path validation guard
        if not case_path:
            def draw_error(self, context):
                self.layout.label(text="Case directory is not set!", icon='ERROR')
                self.layout.label(text="Open the Classy Blocks panel and set the Case Directory.")
            context.window_manager.popup_menu(draw_error, title="No Case Directory", icon='ERROR')
            self.report({'ERROR'}, "Case directory is not set")
            set_status(context, "Failed: Case directory not set")
            return {'CANCELLED'}

        case_path = foam_path_utils.resolve_case_path(case_path)

        if not os.path.isdir(case_path):
            def draw_not_found(self, context):
                self.layout.label(text=f"Case directory not found at '{case_path}'", icon='ERROR')
            context.window_manager.popup_menu(draw_not_found, title="Case Not Found", icon='ERROR')
            self.report({'ERROR'}, f"blockMesh failed: case directory not found at '{case_path}'")
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
        case_path = get_case_path(context)
        bashrc_path = context.preferences.addons[__package__].preferences.bashrc_path

        # Path validation guard
        if not case_path:
            def draw_error(self, context):
                self.layout.label(text="Case directory is not set!", icon='ERROR')
            context.window_manager.popup_menu(draw_error, title="No Case Directory", icon='ERROR')
            self.report({'ERROR'}, "Case directory is not set")
            set_status(context, "Failed: Case directory not set")
            return {'CANCELLED'}

        case_path = foam_path_utils.resolve_case_path(case_path)

        if not os.path.isdir(case_path):
            def draw_not_found(self, context):
                self.layout.label(text=f"Case directory not found at '{case_path}'", icon='ERROR')
            context.window_manager.popup_menu(draw_not_found, title="Case Not Found", icon='ERROR')
            self.report({'ERROR'}, f"foamToVTK failed: case directory not found at '{case_path}'")
            set_status(context, "Failed: Case directory not found")
            return {'CANCELLED'}

        # Check that blockMesh has been run first
        poly_mesh = os.path.join(case_path, "constant", "polyMesh")
        if not os.path.isdir(poly_mesh):
            def draw_no_mesh(self, context):
                self.layout.label(text="polyMesh not found! Run blockMesh first.", icon='ERROR')
            context.window_manager.popup_menu(draw_no_mesh, title="No Mesh Found", icon='ERROR')
            self.report({'ERROR'}, f"polyMesh not found at {poly_mesh} — run blockMesh first (button 2)")
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
        case_path = get_case_path(context)

        # Path validation guard
        if not case_path:
            def draw_error(self, context):
                self.layout.label(text="Case directory is not set!", icon='ERROR')
            context.window_manager.popup_menu(draw_error, title="No Case Directory", icon='ERROR')
            self.report({'ERROR'}, "Case directory is not set")
            set_status(context, "Failed: Case directory not set")
            return {'CANCELLED'}

        case_path = foam_path_utils.resolve_case_path(case_path)

        if not os.path.isdir(case_path):
            def draw_not_found(self, context):
                self.layout.label(text=f"Case directory not found at '{case_path}'", icon='ERROR')
            context.window_manager.popup_menu(draw_not_found, title="Case Not Found", icon='ERROR')
            self.report({'ERROR'}, f"Mesh reload failed: case directory not found at '{case_path}'")
            set_status(context, "Failed: Case directory not found")
            return {'CANCELLED'}

        try:
            vtk_files = vtk_importer.find_vtk_files(case_path)

            if not vtk_files:
                def draw_no_vtk(self, context):
                    self.layout.label(text="No VTK files found! Run foamToVTK first.", icon='ERROR')
                context.window_manager.popup_menu(draw_no_vtk, title="No VTK Files", icon='ERROR')
                self.report({'ERROR'}, f"No VTK files found in {case_path}/VTK/ — run foamToVTK first (button 3)")
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
    """Export selected mesh as STL for terrain projection into the active case"""
    bl_idname = "mesh.classy_export_terrain"
    bl_label = "Export as Terrain STL"

    def execute(self, context):
        scene_props = context.scene.classy_mesh_props
        case_path = get_case_path(context)

        if not case_path:
            def draw_error(self, context):
                self.layout.label(text="Case directory is not set!", icon='ERROR')
            context.window_manager.popup_menu(draw_error, title="No Case Directory", icon='ERROR')
            self.report({'ERROR'}, "Case directory is not set")
            return {'CANCELLED'}

        case_path = foam_path_utils.resolve_case_path(case_path)
        stl_dir = os.path.join(case_path, "constant", "triSurface")
        os.makedirs(stl_dir, exist_ok=True)
        stl_path = os.path.join(stl_dir, "terrain.stl")

        try:
            bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True)
            self.report({'INFO'}, f"Terrain STL exported to {stl_path}")
            set_status(context, f"Exported terrain STL")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export terrain STL: {str(e)}")
            set_status(context, "Failed: STL export error")
            return {'CANCELLED'}


class CLASSY_OT_run_all(bpy.types.Operator):
    """Run the full pipeline: Generate → blockMesh → VTK → Reload"""
    bl_idname = "classy.run_all"
    bl_label = "Run All"

    def execute(self, context):
        context.window.cursor_set('WAIT')
        try:
            # Step 1: Generate blockMeshDict
            result = bpy.ops.classy.generate_mesh()
            if result != {'FINISHED'}:
                self.report({'ERROR'}, "Pipeline stopped: blockMeshDict generation failed")
                set_status(context, "Failed: Generate step")
                return {'CANCELLED'}

            # Step 2: Run blockMesh
            result = bpy.ops.classy.run_blockmesh()
            if result != {'FINISHED'}:
                self.report({'ERROR'}, "Pipeline stopped: blockMesh failed")
                set_status(context, "Failed: blockMesh step")
                return {'CANCELLED'}

            # Step 3: Convert to VTK
            result = bpy.ops.classy.convert_vtk()
            if result != {'FINISHED'}:
                self.report({'ERROR'}, "Pipeline stopped: foamToVTK failed")
                set_status(context, "Failed: VTK step")
                return {'CANCELLED'}

            # Step 4: Reload mesh
            result = bpy.ops.classy.reload_mesh()
            if result != {'FINISHED'}:
                self.report({'ERROR'}, "Pipeline stopped: mesh reload failed")
                set_status(context, "Failed: Reload step")
                return {'CANCELLED'}

            set_status(context, "Success: Full pipeline complete")
            self.report({'INFO'}, "Full pipeline completed successfully")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Pipeline failed: {str(e)}")
            set_status(context, "Failed: Pipeline error")
            import traceback; traceback.print_exc()
            return {'CANCELLED'}
        finally:
            context.window.cursor_set('DEFAULT')
