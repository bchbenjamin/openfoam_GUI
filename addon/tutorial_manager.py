"""
Tutorial Manager.

Allows users to search, browse, and copy official OpenFOAM tutorial cases into
their workspace directly from the Blender interface.
"""

import bpy
import os
import shutil
from pathlib import Path

_tutorials_cache = {}

def get_tutorial_items(self, context):
    scene = context.scene
    # Gracefully handle if foam_dirs isn't registered yet
    if not hasattr(scene, "foam_dirs") or not scene.foam_dirs.foam_tutorials_dir:
        return [("NONE", "Tutorials dir not set", "")]
        
    tut_dir = scene.foam_dirs.foam_tutorials_dir
    tut_path = Path(tut_dir)
    
    if not tut_path.is_dir():
        return [("NONE", "Invalid tutorial path", "")]
        
    # Check cache to avoid freezing Blender with continuous disk I/O on UI redraws
    if tut_dir in _tutorials_cache:
        return _tutorials_cache[tut_dir]
        
    items = []
    
    for root, dirs, files in os.walk(tut_dir):
        if 'system' in dirs:
            system_path = os.path.join(root, 'system')
            if os.path.isdir(system_path):
                rel_path = os.path.relpath(root, tut_dir)
                items.append((rel_path, rel_path, f"Copy {rel_path}"))
            
            # Prune directories to speed up traversal
            dirs.remove('system')
            if 'constant' in dirs: dirs.remove('constant')
            
            for d in ['0', '0.orig', '1', '2', 'processor0', 'Allrun']:
                if d in dirs:
                    dirs.remove(d)

    if not items:
        items = [("NONE", "No tutorials found", "")]
    else:
        items.sort(key=lambda x: x[1])
        
    _tutorials_cache[tut_dir] = items
    return items

class TutorialManagerProperties(bpy.types.PropertyGroup):
    available_tutorials: bpy.props.EnumProperty(
        name="Select Tutorial",
        description="Choose an OpenFOAM tutorial to copy",
        items=get_tutorial_items
    )
    new_case_name: bpy.props.StringProperty(
        name="New Case Name",
        description="Name of the new copied case folder",
        default="my_cavity_case"
    )

class CLASSY_OT_search_tutorials(bpy.types.Operator):
    bl_idname = "mesh.classy_search_tutorials"
    bl_label = "Search Tutorials"
    bl_property = "tutorial_enum"
    
    tutorial_enum: bpy.props.EnumProperty(
        name="Tutorial",
        items=get_tutorial_items
    )
    
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}
        
    def execute(self, context):
        context.scene.tutorial_manager.available_tutorials = self.tutorial_enum
        return {'FINISHED'}

class CLASSY_OT_copy_tutorial(bpy.types.Operator):
    bl_idname = "mesh.classy_copy_tutorial"
    bl_label = "Copy Tutorial Case"
    bl_description = "Copy the selected tutorial to your OpenFOAM run directory"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        tut_props = scene.tutorial_manager
        
        if not hasattr(scene, "foam_dirs"):
            self.report({'ERROR'}, "OpenFOAM directories not configured. Check the Directories panel.")
            return {'CANCELLED'}
            
        run_dir = scene.foam_dirs.foam_run_dir
        tut_dir = scene.foam_dirs.foam_tutorials_dir
        
        if not run_dir or not os.path.isdir(run_dir):
            self.report({'ERROR'}, "Valid FOAM_RUN directory is not set.")
            return {'CANCELLED'}
            
        selected_tut = tut_props.available_tutorials
        if selected_tut == "NONE" or not selected_tut:
            self.report({'ERROR'}, "No valid tutorial selected.")
            return {'CANCELLED'}
            
        src_path = os.path.join(tut_dir, selected_tut)
        if not os.path.isdir(src_path):
            self.report({'ERROR'}, f"Source tutorial path not found: {src_path}")
            return {'CANCELLED'}
            
        case_name = tut_props.new_case_name.strip()
        if not case_name:
            self.report({'ERROR'}, "New case name cannot be empty.")
            return {'CANCELLED'}
            
        dest_path = os.path.join(run_dir, case_name)
        if os.path.exists(dest_path):
            self.report({'ERROR'}, f"Destination already exists: {dest_path}")
            return {'CANCELLED'}
            
        try:
            shutil.copytree(src_path, dest_path)
            self.report({'INFO'}, f"Successfully copied tutorial to {dest_path}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to copy tutorial: {str(e)}")
            return {'CANCELLED'}
        
        # Ask the user if they want to set the active case path
        bpy.ops.classy.confirm_case_path('INVOKE_DEFAULT', dest_path=dest_path)
        return {'FINISHED'}

class CLASSY_OT_confirm_case_path(bpy.types.Operator):
    bl_idname = "classy.confirm_case_path"
    bl_label = "Set as Active Case?"
    bl_description = "Set the newly copied tutorial as the active case directory"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    dest_path: bpy.props.StringProperty()
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)
        
    def draw(self, context):
        layout = self.layout
        layout.label(text="Tutorial copied successfully!", icon='INFO')
        layout.label(text="Do you want to set this as the active case directory?")
        
    def execute(self, context):
        if hasattr(context.scene, "classy_mesh_props"):
            context.scene.classy_mesh_props.case_path = self.dest_path
        if hasattr(context, "area") and context.area:
            context.area.tag_redraw()
        return {'FINISHED'}

class CLASSY_PT_tutorial_manager(bpy.types.Panel):
    bl_label = "Tutorial Manager"
    bl_idname = "CLASSY_PT_tutorial_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Classy FOAM'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        if not hasattr(scene, "tutorial_manager"):
            return
            
        tut_props = scene.tutorial_manager
        
        row = layout.row(align=True)
        # Display current selection on the search button
        current_tut = tut_props.available_tutorials
        btn_text = current_tut if (current_tut and current_tut != "NONE") else "Search & Select Tutorial..."
        
        row.operator("mesh.classy_search_tutorials", text=btn_text, icon='VIEWZOOM')
        
        layout.prop(tut_props, "new_case_name")
        layout.operator("mesh.classy_copy_tutorial", text="Copy to Run Directory", icon='DUPLICATE')

def register():
    bpy.utils.register_class(TutorialManagerProperties)
    bpy.types.Scene.tutorial_manager = bpy.props.PointerProperty(type=TutorialManagerProperties)
    bpy.utils.register_class(CLASSY_OT_search_tutorials)
    bpy.utils.register_class(CLASSY_OT_copy_tutorial)
    bpy.utils.register_class(CLASSY_PT_tutorial_manager)

def unregister():
    bpy.utils.unregister_class(CLASSY_PT_tutorial_manager)
    bpy.utils.unregister_class(CLASSY_OT_copy_tutorial)
    bpy.utils.unregister_class(CLASSY_OT_search_tutorials)
    del bpy.types.Scene.tutorial_manager
    bpy.utils.unregister_class(TutorialManagerProperties)
