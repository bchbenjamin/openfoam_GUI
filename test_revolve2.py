import bpy
import sys
import traceback

sys.path.insert(0, '/home/bchbenjamin/classy_blender_mesh')

try:
    import addon
    from addon import geometry_extractor, properties

    # Register properties so we can use them
    bpy.utils.register_class(properties.ClassyMeshObjectProperties)
    bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=properties.ClassyMeshObjectProperties)

    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.classy_block_props.is_block = True
    obj.classy_block_props.block_type = 'revolve'

    # Deselect active
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')

    spec = geometry_extractor.extract_geometry(bpy.context)
    print("SPEC EXTRACTED OK:", spec['blocks'][0]['type'])
except Exception as e:
    traceback.print_exc()

