import bpy
import time

# Store the time of the last update to implement debouncing
_last_update_time = 0.0
# Flag to indicate if a timer is already scheduled
_timer_scheduled = False

def run_pipeline_if_needed():
    global _timer_scheduled
    _timer_scheduled = False
    
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
        # Run the pipeline
        bpy.ops.classy.run_all()
    except Exception as e:
        print(f"Auto-update failed: {e}")
        
    return None

def auto_update_handler(scene, depsgraph):
    """Depsgraph handler that schedules the auto-update timer."""
    global _last_update_time, _timer_scheduled
    
    # Only care about active updates (geometry changes, object added/removed)
    if not depsgraph.updates:
        return
        
    scene_props = getattr(scene, "classy_mesh_props", None)
    if not scene_props or not scene_props.use_auto_update:
        return
        
    prefs = getattr(bpy.context.preferences.addons.get(__package__), "preferences", None)
    delay = prefs.auto_update_delay if prefs else 2.0
    
    # Record the time of this update
    _last_update_time = time.time()
    
    # If a timer is not already scheduled, schedule one
    if not _timer_scheduled:
        _timer_scheduled = True
        
        # We need a wrapper that checks if the delay has passed since the *last* update
        def timer_wrapper():
            global _timer_scheduled
            now = time.time()
            time_since_last_update = now - _last_update_time
            
            if time_since_last_update >= delay:
                # Enough time has passed with no new updates, run it
                run_pipeline_if_needed()
                return None # Don't run again
            else:
                # Not enough time has passed (a new update came in), reschedule
                return delay - time_since_last_update
                
        bpy.app.timers.register(timer_wrapper, first_interval=delay)

def register():
    if auto_update_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(auto_update_handler)

def unregister():
    if auto_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(auto_update_handler)
