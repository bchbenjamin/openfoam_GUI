import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import bmesh
from mathutils import Vector
from mathutils.geometry import intersect_line_plane
from bpy_extras import view3d_utils

_active_draw_handlers = []


class CLASSY_OT_add_sketch_point(bpy.types.Operator):
    """Interactively draw a sketch (PolyLine or Spline) for Classy Blocks"""
    bl_idname = "classy.add_sketch_point"
    bl_label = "Draw Classy Sketch"
    bl_options = {'REGISTER', 'UNDO'}

    curve_type: bpy.props.EnumProperty(
        name="Curve Type",
        items=[
            ("POLY", "PolyLine (Straight)", "Straight segments"),
            ("BEZIER", "Spline (Smooth)", "Smooth Catmull-Rom spline"),
        ],
        default="POLY"
    )

    sketch_plane: bpy.props.EnumProperty(
        name="Sketch Plane",
        items=[
            ("XY", "XY Plane (Ground)", "Draw on the flat ground plane"),
            ("XZ", "XZ Plane (Front)", "Draw upright facing front (good for Revolve)"),
            ("YZ", "YZ Plane (Side)", "Draw upright facing side"),
        ],
        default="XY",
        description="Select which plane to draw the sketch on (used as fallback when not clicking on geometry)"
    )

    def __init__(self) -> None:
        self._points = []
        self._mouse_pos = (0, 0)
        self._draw_handle = None
        self._shader = gpu.shader.from_builtin('UNIFORM_COLOR')

    def _cleanup(self, context) -> None:
        """

        Args:
          context: 

        Returns:

        """
        if self._draw_handle is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle, 'WINDOW')
            except ValueError:
                pass
            if self._draw_handle in _active_draw_handlers:
                _active_draw_handlers.remove(self._draw_handle)
            self._draw_handle = None

        context.area.tag_redraw()

    def _get_3d_location(self, context, event):
        """Raycast into the scene, fallback to Z=0 plane.

        Args:
          context: 
          event: 

        Returns:

        """
        # Convert raw window coordinates into region coordinates safely
        coord = (
            event.mouse_x - self._region.x,
            event.mouse_y - self._region.y
        )

        view_vector = view3d_utils.region_2d_to_vector_3d(self._region, self._rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(self._region, self._rv3d, coord)

        # 1. Raycast against scene geometry
        depsgraph = context.evaluated_depsgraph_get()
        hit, location, normal, index, obj, matrix = context.scene.ray_cast(
            depsgraph, ray_origin, view_vector
        )

        if hit:
            pt = location.copy()
        else:
            # 2. Fallback to chosen sketch plane
            plane_co = Vector((0.0, 0.0, 0.0))
            if self.sketch_plane == 'XZ':
                plane_no = Vector((0.0, 1.0, 0.0))
            elif self.sketch_plane == 'YZ':
                plane_no = Vector((1.0, 0.0, 0.0))
            else:
                plane_no = Vector((0.0, 0.0, 1.0))
                
            pt = intersect_line_plane(ray_origin, ray_origin + view_vector, plane_co, plane_no)
            if pt is None:
                pt = Vector((0.0, 0.0, 0.0))

        # 3. Grid Snapping
        if event.ctrl:
            # Snap to nearest 0.1m for now (can read scene units if needed)
            snap = 0.1
            pt.x = round(pt.x / snap) * snap
            pt.y = round(pt.y / snap) * snap
            pt.z = round(pt.z / snap) * snap

        return pt

    def modal(self, context, event):
        """

        Args:
          context: 
          event: 

        Returns:

        """
        context.area.tag_redraw()

        try:
            if event.type == 'MOUSEMOVE':
                self._mouse_pos = (event.mouse_region_x, event.mouse_region_y)
                self._current_3d = self._get_3d_location(context, event)
                
            elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                pt = self._get_3d_location(context, event)
                self._points.append(pt)
                return {'RUNNING_MODAL'}
                
            elif event.type in {'RET', 'NUMPAD_ENTER', 'SPACE'}:
                # Finish sketch
                if len(self._points) >= 2:
                    self._create_curve(context)
                self._cleanup(context)
                return {'FINISHED'}
                
            elif event.type in {'RIGHTMOUSE', 'ESC'}:
                self._cleanup(context)
                return {'CANCELLED'}

        except Exception as e:
            self._cleanup(context)
            self.report({'ERROR'}, f"Sketch tool failed: {e}")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def _create_curve(self, context) -> None:
        """

        Args:
          context: 

        Returns:

        """
        curve_data = bpy.data.curves.new(name="ClassySketch", type='CURVE')
        curve_data.dimensions = '3D'
        
        spline = curve_data.splines.new(self.curve_type)
        spline.points.add(len(self._points) - 1)
        
        for i, pt in enumerate(self._points):
            # For POLY and BEZIER splines, the structure slightly differs in Blender
            if self.curve_type == 'POLY':
                spline.points[i].co = (pt.x, pt.y, pt.z, 1.0)
            elif self.curve_type == 'BEZIER':
                # But actually, Blender Splines can be type 'BEZIER' or 'POLY' or 'NURBS'
                # For Bezier we must use bezier_points
                # To keep it simple, we just use POLY or NURBS (which behaves like Catmull-Rom if set up right).
                # Wait, spline.type = 'BEZIER' requires bezier_points.
                # Let's just create a POLY, or NURBS. 
                pass

        # Handle BEZIER properly
        if self.curve_type == 'BEZIER':
            # Remove the auto-created POLY points if changing type
            spline.type = 'BEZIER'
            spline.bezier_points.add(len(self._points) - 1)
            for i, pt in enumerate(self._points):
                spline.bezier_points[i].co = pt
                spline.bezier_points[i].handle_left_type = 'AUTO'
                spline.bezier_points[i].handle_right_type = 'AUTO'
        
        obj = bpy.data.objects.new("ClassySketch", curve_data)
        context.collection.objects.link(obj)
        
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Tag for geometry extractor
        obj["classy_sketch"] = True
        obj["classy_shape_type"] = "sketch"

        bpy.ops.ed.undo_push(message="Add Classy Sketch")

    def invoke(self, context, event):
        """

        Args:
          context: 
          event: 

        Returns:

        """
        if context.area.type == 'VIEW_3D':
            self._region = next((r for r in context.area.regions if r.type == 'WINDOW'), context.region)
            self._rv3d = context.space_data.region_3d

            self._points = []
            self._current_3d = Vector((0, 0, 0))
            self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_callback_3d, (context,), 'WINDOW', 'POST_VIEW'
            )
            _active_draw_handlers.append(self._draw_handle)
            
            context.window_manager.modal_handler_add(self)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found")
            return {'CANCELLED'}

    def draw_callback_3d(self, context) -> None:
        """

        Args:
          context: 

        Returns:

        """
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(3.0)
        
        coords = self._points[:]
        if hasattr(self, '_current_3d'):
            coords.append(self._current_3d)
            
        if len(coords) >= 2:
            batch = batch_for_shader(self._shader, 'LINE_STRIP', {"pos": coords})
            self._shader.uniform_float("color", (1.0, 0.5, 0.0, 1.0))
            batch.draw(self._shader)
            
        # Draw points
        if len(coords) >= 1:
            gpu.state.point_size_set(6.0)
            batch_pts = batch_for_shader(self._shader, 'POINTS', {"pos": coords})
            self._shader.uniform_float("color", (1.0, 0.8, 0.1, 1.0))
            batch_pts.draw(self._shader)
            
        gpu.state.blend_set('NONE')

def unregister_handlers() -> None:
    """ """
    for handler in _active_draw_handlers:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        except ValueError:
            pass
    _active_draw_handlers.clear()
