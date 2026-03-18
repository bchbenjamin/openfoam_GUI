import bpy
import sys

# Add our project dir to path
sys.path.insert(0, '/home/bchbenjamin/classy_blender_mesh')

try:
    from addon import geometry_extractor
    
    # Create an object
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.classy_block_props = type('MockProps', (), {
        'is_block': True,
        'block_type': 'revolve',
        'revolve_face_index': 0,
        'revolve_angle': 90.0,
        'revolve_axis': [0,1,0],
        'revolve_origin': [0,0,0],
        'cells': [10,10,10],
        'grading': [1,1,1],
        'patch_name': 'test'
    })()

    # Deselect the object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = None

    spec = geometry_extractor.extract_geometry(bpy.context)
    print("SPEC EXTRACTED OK:", spec['blocks'][0]['type'])
except Exception as e:
    import traceback
    traceback.print_exc()

