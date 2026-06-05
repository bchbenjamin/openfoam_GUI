import bpy
import time

# Store the time of the last update to implement debouncing
_last_update_time = 0.0
# Flag to indicate if a timer is already scheduled
_timer_scheduled = False
# Lock to prevent infinite depsgraph update loops during VTK import
is_auto_updating = False

def run_pipeline_if_needed():
    global _timer_scheduled, is_auto_updating
    _timer_scheduled = False
    
    if is_auto_updating:
        return None
        
    context = bpy.context
    if not hasattr(context, "scene") or not context.scene:
        return None
        
    scene_props = getattr(context.scene, "classy_mesh_props", None)
    if not scene_props or not scene_props.use_auto_update:
        return None
        
    prefs = getattr(context.preferences.addons.get(__package__), "preferences", None)
    if not prefs:
        return None

    # Check block limit
    mesh_objects = [o for o in context.scene.objects if o.type == 'MESH']
    excluded = sum(1 for o in mesh_objects
                   if getattr(o, "classy_block_props", None)
                   and o.classy_block_props.exclude_from_mesh)
    active_blocks = len(mesh_objects) - excluded
    
    if active_blocks > prefs.auto_update_limit:
        return None # Too many blocks, skip auto-update
        
    # Check if case path is set
    if not scene_props.case_path:
        return None
        
    try:
        is_auto_updating = True
        # Run the pipeline
        bpy.ops.classy.run_all()
    except Exception as e:
        print(f"Auto-update failed: {e}")
    finally:
        is_auto_updating = False
        
    return None

def trigger_update_timer(delay):
    global _last_update_time, _timer_scheduled
    _last_update_time = time.time()
    
    if not _timer_scheduled:
        _timer_scheduled = True
        
        def timer_wrapper():
            global _timer_scheduled
            now = time.time()
            time_since_last_update = now - _last_update_time
            
            if time_since_last_update >= delay:
                run_pipeline_if_needed()
                return None
            else:
                return delay - time_since_last_update
                
        bpy.app.timers.register(timer_wrapper, first_interval=delay)

@bpy.app.handlers.persistent
def auto_update_handler(scene, depsgraph):
    """Depsgraph handler that schedules the auto-update timer."""
    if is_auto_updating:
        return
        
    # Only care about active updates (geometry changes, object added/removed)
    if not depsgraph.updates:
        return
        
    scene_props = getattr(scene, "classy_mesh_props", None)
    if not scene_props or not scene_props.use_auto_update:
        return
        
    prefs = getattr(bpy.context.preferences.addons.get(__package__), "preferences", None)
    delay = prefs.auto_update_delay if prefs else 2.0
    
    trigger_update_timer(delay)

@bpy.app.handlers.persistent
def undo_handler(scene, *args):
    """Handler to trigger auto-update on Undo"""
    if is_auto_updating:
        return
        
    scene_props = getattr(scene, "classy_mesh_props", None)
    if not scene_props or not scene_props.use_auto_update:
        return
        
    prefs = getattr(bpy.context.preferences.addons.get(__package__), "preferences", None)
    delay = prefs.auto_update_delay if prefs else 2.0
    
    trigger_update_timer(delay)

def register():
    if auto_update_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(auto_update_handler)
    if undo_handler not in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.append(undo_handler)

def unregister():
    if auto_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(auto_update_handler)
    if undo_handler in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.remove(undo_handler)
