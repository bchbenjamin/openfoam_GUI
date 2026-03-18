import bpy
import sys
import traceback

sys.path.insert(0, '/home/bchbenjamin/classy_blender_mesh')

try:
    import addon
    from addon import geometry_extractor, properties, mesh_builder
    import os, tempfile

    # Register properties
    bpy.utils.register_class(properties.ClassyMeshObjectProperties)
    bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=properties.ClassyMeshObjectProperties)

    # Add a plane
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.classy_block_props.is_block = True
    obj.classy_block_props.block_type = 'extrude'
    # By default extrude_face_index = 0

    # Deselect active
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')

    spec = geometry_extractor.extract_geometry(bpy.context)
    print("SPEC EXTRACTED OK:", spec['blocks'][0]['type'])
    
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, 'system'))
        bmd = os.path.join(td, 'system', 'blockMeshDict')
        mesh_builder.build_from_spec(spec, bmd)
        print("MESH BUILDER OK")
except Exception as e:
    traceback.print_exc()

