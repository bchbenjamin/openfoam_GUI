"""
Blender Operators for the Classy Blocks add-on.

Contains the execution logic for user actions (buttons), such as tagging shapes,
running blockMesh, executing foamToVTK, and managing the overall pipeline.
"""

import os
import datetime
import bpy
from . import mesh_builder, foam_runner, geometry_extractor, vtk_importer, case_setup
from . import foam_path_utils
from . import auto_update as _auto_update

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
            # Try explicit default first, then last-used
            case_path = prefs.default_case_dir or prefs.last_case_dir
    return case_path


def _save_last_case_dir(context, case_path):
    """Persist the last-used case directory into AddonPreferences."""
    try:
        prefs = context.preferences.addons[__package__].preferences
        if case_path and case_path != prefs.last_case_dir:
            prefs.last_case_dir = case_path
    except (KeyError, TypeError, AttributeError):
        pass

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
                warning_msg = "Skipped objects: " + " | ".join(
                    w for w in warnings[:4]
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

            # Guarantee all STL files are present in the case directory
            import shutil
            for block in meshable_blocks:
                if "stl_projections" in block and "stl_absolute_path" in block:
                    stl_abs = block["stl_absolute_path"]
                    stl_base = block["stl_projections"][list(block["stl_projections"].keys())[0]]
                    
                    if not os.path.isfile(stl_abs):
                        self.report({'ERROR'}, f"STL file not found at '{stl_abs}' (referenced by block '{block.get('name', 'Unknown')}')")
                        set_status(context, "Failed: STL file not found")
                        return {'CANCELLED'}
                        
                    # blockMesh requires the STL to be in constant/geometry for searchableSurface (as confirmed by the OpenFOAM IO error).
                    # SnappyHexMesh often looks in constant/triSurface by default.
                    # We copy to both locations for full compatibility with OF meshing tools.
                    stl_dir_geom = os.path.join(case_path, "constant", "geometry")
                    stl_dir_tri = os.path.join(case_path, "constant", "triSurface")
                    os.makedirs(stl_dir_geom, exist_ok=True)
                    os.makedirs(stl_dir_tri, exist_ok=True)
                    
                    dest_geom = os.path.join(stl_dir_geom, stl_base)
                    dest_tri = os.path.join(stl_dir_tri, stl_base)
                    
                    source_size = os.path.getsize(stl_abs)
                    
                    # Smart copy: avoid redundant I/O for large STL files
                    for dest in (dest_geom, dest_tri):
                        if not os.path.exists(dest) or os.path.getsize(dest) != source_size:
                            shutil.copy2(stl_abs, dest)

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
            _save_last_case_dir(context, case_path)
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
        try:
            bashrc_path = context.preferences.addons[__package__].preferences.bashrc_path
        except (KeyError, TypeError):
            bashrc_path = ""

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
        try:
            bashrc_path = context.preferences.addons[__package__].preferences.bashrc_path
        except (KeyError, TypeError):
            bashrc_path = ""

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
        stl_dir1 = os.path.join(case_path, "constant", "triSurface")
        stl_dir2 = os.path.join(case_path, "constant", "geometry")
        os.makedirs(stl_dir1, exist_ok=True)
        os.makedirs(stl_dir2, exist_ok=True)
        
        stl_path1 = os.path.join(stl_dir1, "terrain.stl")
        stl_path2 = os.path.join(stl_dir2, "terrain.stl")

        try:
            bpy.ops.wm.stl_export(filepath=stl_path1, export_selected_objects=True)
            import shutil
            shutil.copy2(stl_path1, stl_path2)
            self.report({'INFO'}, f"Terrain STL exported to {stl_path1} & {stl_path2}")
            set_status(context, f"Exported terrain STL")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export terrain STL: {str(e)}")
            set_status(context, "Failed: STL export error")
            return {'CANCELLED'}


class CLASSY_OT_project_to_stl(bpy.types.Operator):
    """Validate the selected STL file for projection"""
    bl_idname = "classy.project_to_stl"
    bl_label = "Validate STL Projection"

    def execute(self, context):
        set_status(context, "Validating STL...")
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object")
            set_status(context, "Failed: No active mesh object")
            return {'CANCELLED'}

        props = obj.classy_block_props
        stl_path = props.stl_file

        # Path validation guard
        if not stl_path:
            def draw_error(self, context):
                self.layout.label(text="STL File is not set!", icon='ERROR')
            context.window_manager.popup_menu(draw_error, title="No STL File", icon='ERROR')
            self.report({'ERROR'}, "STL File is not set")
            set_status(context, "Failed: STL File not set")
            return {'CANCELLED'}

        stl_path = bpy.path.abspath(stl_path)

        if not os.path.isfile(stl_path):
            def draw_not_found(self, context):
                self.layout.label(text=f"STL file not found at '{stl_path}'", icon='ERROR')
            context.window_manager.popup_menu(draw_not_found, title="STL Not Found", icon='ERROR')
            self.report({'ERROR'}, f"STL validation failed: file not found at '{stl_path}'")
            set_status(context, "Failed: STL file not found")
            return {'CANCELLED'}

        try:
            from . import stl_projector
            result = stl_projector.validate_stl(stl_path)

            if not result["valid"]:
                self.report({'ERROR'}, f"STL validation failed: {result['error']}")
                set_status(context, "Failed: STL invalid")
                return {'CANCELLED'}

            for warning in result.get("warnings", []):
                self.report({'WARNING'}, warning)

            info_msg = f"STL Valid ({result['n_triangles']} triangles, manifold={result['is_manifold']})"
            self.report({'INFO'}, info_msg)
            set_status(context, "Success: STL valid")
            return {'FINISHED'}

        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
            set_status(context, "Failed: FileNotFoundError")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'},
                        f"STL validation execution failed: {str(e)}")
            set_status(context, "Failed: STL validation exception")
            return {'CANCELLED'}


class CLASSY_OT_run_all(bpy.types.Operator):
    """Run the full pipeline: Generate → blockMesh → VTK → Reload"""
    bl_idname = "classy.run_all"
    bl_label = "Run All"

    def execute(self, context):
        context.window.cursor_set('WAIT')
        # Hold the auto-update lock for the entire pipeline so the depsgraph
        # changes from VTK mesh import don't schedule a second run.
        _auto_update.is_auto_updating = True
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
            _auto_update.is_auto_updating = False
            context.window.cursor_set('DEFAULT')

class CLASSY_OT_extrude_sketch(bpy.types.Operator):
    """Extrude a 4-point sketch into a 3D block"""
    bl_idname = "classy.extrude_sketch"
    bl_label = "Extrude Sketch"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'CURVE' and obj.get("classy_sketch")

    def execute(self, context):
        obj = context.active_object
        curve = obj.data
        if not curve.splines:
            self.report({'WARNING'}, "Sketch is empty.")
        else:
            spline = curve.splines[0]
            num_pts = len(spline.bezier_points) if spline.type == 'BEZIER' else len(spline.points)
            if num_pts != 4:
                self.report({'WARNING'}, f"Sketch has {num_pts} points. Extrude requires exactly 4 points.")
            else:
                self.report({'INFO'}, "Sketch tagged for Extrusion")
                
        obj.classy_block_props.block_type = 'EXTRUDE'
        return {'FINISHED'}

class CLASSY_OT_revolve_sketch(bpy.types.Operator):
    """Revolve a 4-point sketch into a 3D block"""
    bl_idname = "classy.revolve_sketch"
    bl_label = "Revolve Sketch"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'CURVE' and obj.get("classy_sketch")

    def execute(self, context):
        obj = context.active_object
        curve = obj.data
        if not curve.splines:
            self.report({'WARNING'}, "Sketch is empty.")
        else:
            spline = curve.splines[0]
            num_pts = len(spline.bezier_points) if spline.type == 'BEZIER' else len(spline.points)
            if num_pts != 4:
                self.report({'WARNING'}, f"Sketch has {num_pts} points. Revolve requires exactly 4 points.")
            else:
                self.report({'INFO'}, "Sketch tagged for Revolution")
                
        obj.classy_block_props.block_type = 'REVOLVE'
        return {'FINISHED'}

class CLASSY_OT_tag_extrude(bpy.types.Operator):
    """Tag the active quad face for extrusion"""
    bl_idname = "classy.tag_extrude"
    bl_label = "Tag as Extrude Block"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and context.active_object

    def execute(self, context):
        import bmesh
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        
        active_face = bm.faces.active
        if not active_face or not active_face.select:
            # Fallback to finding a selected face
            selected_faces = [f for f in bm.faces if f.select]
            if not selected_faces:
                self.report({'ERROR'}, "No face selected. Please select a quad face.")
                return {'CANCELLED'}
            active_face = selected_faces[0]

        if len(active_face.verts) != 4:
            self.report({'ERROR'}, "If you want a circular 3D pipe, you do not draw a circle. You must use the built-in Cylinder primitive, which automatically generates the complex 12-block 'O-grid' required for round structured meshes.")
            return {'CANCELLED'}
            
        face_index = active_face.index
        
        # Tag it
        props = obj.classy_block_props
        props.block_type = 'EXTRUDE'
        props.extrude_face_index = face_index
        
        self.report({'INFO'}, f"Tagged Face {face_index} for Extrusion")
        return {'FINISHED'}

class CLASSY_OT_tag_revolve(bpy.types.Operator):
    """Tag the active quad face for revolution"""
    bl_idname = "classy.tag_revolve"
    bl_label = "Tag as Revolve Block"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and context.active_object

    def execute(self, context):
        import bmesh
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        
        active_face = bm.faces.active
        if not active_face or not active_face.select:
            selected_faces = [f for f in bm.faces if f.select]
            if not selected_faces:
                self.report({'ERROR'}, "No face selected. Please select a quad face.")
                return {'CANCELLED'}
            active_face = selected_faces[0]

        if len(active_face.verts) != 4:
            self.report({'ERROR'}, "If you want a circular 3D pipe, you do not draw a circle. You must use the built-in Cylinder primitive, which automatically generates the complex 12-block 'O-grid' required for round structured meshes.")
            return {'CANCELLED'}
            
        face_index = active_face.index
        
        props = obj.classy_block_props
        props.block_type = 'REVOLVE'
        props.revolve_face_index = face_index
        
        self.report({'INFO'}, f"Tagged Face {face_index} for Revolution")
        return {'FINISHED'}

class CLASSY_OT_tag_loft(bpy.types.Operator):
    """Tag two active quad faces for lofting"""
    bl_idname = "classy.tag_loft"
    bl_label = "Tag as Loft Block"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and context.active_object

    def execute(self, context):
        import bmesh
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        
        selected_faces = [f for f in bm.faces if f.select]
        if len(selected_faces) != 2:
            self.report({'ERROR'}, f"Lofting requires exactly 2 selected faces. You have {len(selected_faces)} selected.")
            return {'CANCELLED'}
            
        for face in selected_faces:
            if len(face.verts) != 4:
                self.report({'ERROR'}, "If you want a circular 3D pipe, you do not draw a circle. You must use the built-in Cylinder primitive, which automatically generates the complex 12-block 'O-grid' required for round structured meshes.")
                return {'CANCELLED'}
        
        face_index_1 = selected_faces[0].index
        face_index_2 = selected_faces[1].index
        
        props = obj.classy_block_props
        props.block_type = 'LOFT'
        props.loft_bottom_face_index = face_index_1
        props.loft_top_face_index = face_index_2
        
        self.report({'INFO'}, f"Tagged Faces {face_index_1} and {face_index_2} for Lofting")
        return {'FINISHED'}

class CLASSY_OT_add_boundary_patch(bpy.types.Operator):
    """Add a new boundary condition for a side"""
    bl_idname = "classy.add_boundary_patch"
    bl_label = "Add Boundary"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and hasattr(context.active_object, "classy_block_props")

    def execute(self, context):
        props = context.active_object.classy_block_props
        new_patch = props.face_patches.add()
        
        # Set default side name based on block type if possible
        if props.block_type in ("CYLINDER", "FRUSTUM", "EXTRUDED_RING"):
            new_patch.side_name = "outer"
        elif props.block_type in ("BOX",):
            new_patch.side_name = "top"
        else:
            new_patch.side_name = "bottom"
            
        props.active_face_patch_index = len(props.face_patches) - 1
        return {'FINISHED'}

class CLASSY_OT_remove_boundary_patch(bpy.types.Operator):
    """Remove the selected boundary condition"""
    bl_idname = "classy.remove_boundary_patch"
    bl_label = "Remove Boundary"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj or not hasattr(obj, "classy_block_props"):
            return False
        return len(obj.classy_block_props.face_patches) > 0

    def execute(self, context):
        props = context.active_object.classy_block_props
        idx = props.active_face_patch_index
        props.face_patches.remove(idx)
        props.active_face_patch_index = max(0, idx - 1)
        return {'FINISHED'}

class CLASSY_OT_add_box(bpy.types.Operator):
    """Add a Cube and tag it as a Classy Box"""
    bl_idname = "classy.add_box"
    bl_label = "Add Box Primitive"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        if context.active_object:
            context.active_object.classy_block_props.block_type = 'BOX'
        return {'FINISHED'}

class CLASSY_OT_add_cylinder(bpy.types.Operator):
    """Add a Cylinder and tag it as a Classy Cylinder"""
    bl_idname = "classy.add_cylinder"
    bl_label = "Add Cylinder Primitive"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_cylinder_add()
        if context.active_object:
            context.active_object.classy_block_props.block_type = 'CYLINDER'
        return {'FINISHED'}

class CLASSY_OT_add_frustum(bpy.types.Operator):
    """Add a Cone/Frustum and tag it as a Classy Frustum"""
    bl_idname = "classy.add_frustum"
    bl_label = "Add Frustum Primitive"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_cone_add(radius1=1.0, radius2=0.5)
        if context.active_object:
            context.active_object.classy_block_props.block_type = 'FRUSTUM'
        return {'FINISHED'}
