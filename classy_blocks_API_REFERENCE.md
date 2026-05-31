# Python API Reference: classy_blocks

This section covers the comprehensive API reference for all classes and functions exposed by the `classy_blocks` library.

## Classes

### `class AnalyticCurve`

A parametric curve, defined by a user-specified function

`P = f(t)`

**Constructor:** `AnalyticCurve(function: Callable[[float], nptyping.ndarray.NDArray], bounds: tuple[float, float])`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `discretize(self, param_from: Optional[float] = None, param_to: Optional[float] = None, count: int = 15) -> NDArray[Shape['*, 3'], Any]`: Discretized the curve into 'count' points.
- `get_binormal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns the binormal vector from Frenet-Serret TNB frame (https://en.wikipedia.org/wiki/Frenet%E2%80%93Serret_formulas)
- `get_closest_param(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> float`: Finds the param on curve where point is the closest to given point
- `get_closest_point(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> NDArray[Shape['3, 1'], Any]`
- `get_length(self, param_from: Optional[float] = None, param_to: Optional[float] = None) -> float`: Returns the length of the curve between the given parameters; bounds are used if they are not supplied.
- `get_normal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximated normal vector at given parameter
- `get_param_at_length(self, length: float) -> float`: Returns parameter at specified length along the curve
- `get_point(self, param: float) -> NDArray[Shape['3, 1'], Any]`: Returns point at given parameter
- `get_tangent(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximate, normalized tangent to the curve at given parameter
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Angle`

Parameters for an arc edge, alternative definition
by Foundation (.org); defined with sector angle and axis

https://github.com/OpenFOAM/OpenFOAM-10/commit/73d253c34b3e184802efb316f996f244cc795ec6

All arc variants are supported by classy_blocks;
however, only the first (classic) one will be written to blockMeshDict for compatibility.
If an edge was specified by 'angle' or 'origin', the definition will be output as a comment
next to that edge definition.

**Constructor:** `Angle(angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self, ratio, origin=None)`: Axis is not to be scaled
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self, displacement)`: Axis is not to be translated

---

### `class Arc`

Parameters for an arc edge: classic OpenFOAM circular arc
definition with a single point lying anywhere on the arc

**Constructor:** `Arc(arc_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Assembly`

Base class for mesh-building elements and tools
for manipulation thereof.

**Constructor:** `Assembly(shapes: collections.abc.Sequence[classy_blocks.construct.shape.Shape])`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Box`

A Rudimentary Box with edges aligned to
cartesian coordinates x-y-z. Refer to sketch
in blockMesh documentation for explanation of args below:
https://doc.cfd.direct/openfoam/user-guide-v6/blockmesh
https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility

Args:
- start_point: one corner of the box
- diagonal_point: corner at the other end of volumetric diagonal to start_point;

Box() will always sort input data so that it becomes aligned with
cartesian coordinate system. Therefore edge 0-1 will correspond to x-axis,
1-2 to y- and 0-4 to z-axis.

**Constructor:** `Box(start_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], diagonal_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `add_side_edge(self, corner_idx: int, edge_data: classy_blocks.construct.edges.EdgeData) -> None`: Add an edge between two vertices at the same corner of the lower and upper face (index and index+4 or vice versa).
- `chop(self, axis: Literal[0, 1, 2], **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`: Chop the whole operation (set cell count and optional grading) in one direction. Parameters ---------- Axis : int Direction in which to apply the chop: * **0** - along the first edge of a face * **1** - along the second edge of a face * **2** - between faces / along the operation path Keyword arguments ---------------- start_size : float, optional Width of the first cell. end_size : float, optional Width of the last cell. count : int, optional Number of cells in the chosen direction. c2c_expansion : float, optional Cell-to-cell expansion ratio (default = 1). total_expansion : float, optional Ratio between the first and last cell size. take : optional Edge length to use when computing the cell count. Use 'min', 'max' or 'avg' (the default) preserve : optional Which parameter to maintain consistent when distributing chops to other blocks in the same row. Can be ``c2c_expansion``, ``start_size`` or ``end_size``. The default is ``total_expansion``. length_ratio : optional To use multi-graded blocks, add multiple chops to the same axis by calling ``.chop()`` multiple times. Each chop takes a fraction of length (should total to 1) which is specified by ``length_ratio``. https://cfd.direct/openfoam/user-guide/v9-blockMesh/#multi-grading Notes ----- * Specify one or two chopping parameters (start/end size, c2c expansion, total expansion, count). That specifies grading completely. Using more than two makes the calculation over-defined and will yield inconsistent results or will throw an exception. * When only one parameter is given, ``c2c_expansion`` defaults to 1 and a uniform cell size is produced. * ``total_expansion`` cannot be used with ``c2c_expansion`` = 1. * ``take`` controls which edge length in given axis is taken when calculating grading.
- `chop_edge(self, corner_1: int, corner_2: int, **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `from_series(faces: list[classy_blocks.construct.flat.face.Face]) -> 'Operation'`: Creates a Loft from a list of faces. At least two are required. From faces in between, side edges are created: - 2 faces: no side edges - 3: Arcs - 4 or more: Splines
- `get_all_faces(self) -> dict[typing.Literal['left', 'right', 'front', 'back', 'top', 'bottom'], classy_blocks.construct.flat.face.Face]`: Returns a list of all faces
- `get_closest_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has a center nearest to given point
- `get_closest_side(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> Literal['left', 'right', 'front', 'back', 'top', 'bottom']`: Returns side (bottom/top/left/right/front/back) of the closest face to given point
- `get_face(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> classy_blocks.construct.flat.face.Face`: Returns a new Face on specified side of the Operation. Warning: bottom, left and front faces must be inverted prior to using them for a loft/extrude etc (they point inside the operation by default).
- `get_index_from_side(side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> int`: Returns index of edges/patches/projections from given orient
- `get_normal_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has normal closest to vector that connects returned face and 'point' (viewer).
- `get_patches_at_corner(self, corner: int) -> set`: Returns patch names at given corner (up to 3)
- `invert(self) -> 'Operation'`: Flips top and bottom face
- `mirror(self, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Mirroring an operation will create an inside-out block but automatic reordering of all vertices would create confusion. To avoid both, bottom and top face are swapped after mirroring so that original and mirrored lofts face the same z-direction.
- `project_corner(self, corner: int, label: Union[str, list[str]]) -> None`: Project the vertex at given corner (local index 0...7) to a single surface or an intersection of multiple surface. WIP according to https://github.com/OpenFOAM/OpenFOAM-10/blob/master/src/meshTools/searchableSurfaces/searchableSurfacesQueries/searchableSurfacesQueries.H
- `project_edge(self, corner_1: int, corner_2: int, label: Union[str, list[str]]) -> None`: Replace an edge between given corners with a Projected one or add geometry to an already projected edge
- `project_side(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom'], label: str, edges: bool = False, points: bool = False) -> None`: Project given side to a labeled geometry; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right'; the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - label: name of predefined geometry (add separately to Mesh object) - edges:if True, all edges belonging to this side will also be projected
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Assign a cellZone to this block.
- `set_patch(self, sides: Union[Literal['left', 'right', 'front', 'back', 'top', 'bottom'], list[Literal['left', 'right', 'front', 'back', 'top', 'bottom']]], name: str) -> None`: Assign a patch to given side of the block; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right', a single value or a list of sides; names correspond to position in the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - name: the name that goes into blockMeshDict Use mesh.set_patch_* methods to change other properties (type and other settings)
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self, transforms)`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `unchop(self, axis: Optional[Literal[0, 1, 2]] = None) -> None`: Removes existing chops from an operation (comes handy after copying etc.)

---

### `class CircleCurve`

A parametric circle, defined by center, starting point and normal.
A full circle is valid by default. Provide custom bounds to clip
this curve to an arc.

**Constructor:** `CircleCurve(origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], rim: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], bounds: tuple[float, float] = (0, 6.283185307179586))`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `discretize(self, param_from: Optional[float] = None, param_to: Optional[float] = None, count: int = 15) -> NDArray[Shape['*, 3'], Any]`: Discretized the curve into 'count' points.
- `get_binormal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns the binormal vector from Frenet-Serret TNB frame (https://en.wikipedia.org/wiki/Frenet%E2%80%93Serret_formulas)
- `get_closest_param(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> float`: Finds the param on curve where point is the closest to given point
- `get_closest_point(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> NDArray[Shape['3, 1'], Any]`
- `get_length(self, param_from: Optional[float] = None, param_to: Optional[float] = None) -> float`: Returns the length of the curve between the given parameters; bounds are used if they are not supplied.
- `get_normal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximated normal vector at given parameter
- `get_param_at_length(self, length: float) -> float`: Returns parameter at specified length along the curve
- `get_point(self, param: float) -> NDArray[Shape['3, 1'], Any]`: Returns point at given parameter
- `get_tangent(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximate, normalized tangent to the curve at given parameter
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class ClampBase`

Movement restriction for optimization by vertex movement

**Constructor:** `ClampBase(position: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], function: Callable[[list[float]], nptyping.ndarray.NDArray], bounds: Optional[list[list[float]]] = None, initial_params: Optional[list[float]] = None)`


**Methods:**

- `get_params(self) -> list[float]`: Returns parameters from initial vertex position
- `update_params(self, params: list[float])`: Updates parameters to given.

---

### `class Connector`

A normal Loft but automatically finds and reorders appropriate faces between
two arbitrary given blocks.

The recipe is as follows:
  1. Find a pair of faces whose normals are most nicely aligned
  2. Create a loft that connects them
  3. Reorder the loft so that is is properly oriented

The following limitations apply:
"Closest faces" might be an ill-defined term; for example,
imagine two boxes:
      ___
     | 2 |
     |___|
 ___
| 1 |
|___|

Here, multiple different faces can be found.

Reordering relies on ViewpointReorienter; see the documentation on that
for its limitations.

Resulting loft will have the bottom face coincident with operation_1
and top face with operation_2.
Axis 2 is always between the two operations but axes 0 and 1
depend on positions of operations and is not exactly defined.
To somewhat alleviate this confusion it is
recommended to chop operation 1 or 2 in axes 0 and 1 and
only provide chopping for axis 2 of connector.

**Constructor:** `Connector(operation_1: classy_blocks.construct.operations.operation.Operation, operation_2: classy_blocks.construct.operations.operation.Operation)`


**Methods:**

- `add_side_edge(self, corner_idx: int, edge_data: classy_blocks.construct.edges.EdgeData) -> None`: Add an edge between two vertices at the same corner of the lower and upper face (index and index+4 or vice versa).
- `chop(self, axis: Literal[0, 1, 2], **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`: Chop the whole operation (set cell count and optional grading) in one direction. Parameters ---------- Axis : int Direction in which to apply the chop: * **0** - along the first edge of a face * **1** - along the second edge of a face * **2** - between faces / along the operation path Keyword arguments ---------------- start_size : float, optional Width of the first cell. end_size : float, optional Width of the last cell. count : int, optional Number of cells in the chosen direction. c2c_expansion : float, optional Cell-to-cell expansion ratio (default = 1). total_expansion : float, optional Ratio between the first and last cell size. take : optional Edge length to use when computing the cell count. Use 'min', 'max' or 'avg' (the default) preserve : optional Which parameter to maintain consistent when distributing chops to other blocks in the same row. Can be ``c2c_expansion``, ``start_size`` or ``end_size``. The default is ``total_expansion``. length_ratio : optional To use multi-graded blocks, add multiple chops to the same axis by calling ``.chop()`` multiple times. Each chop takes a fraction of length (should total to 1) which is specified by ``length_ratio``. https://cfd.direct/openfoam/user-guide/v9-blockMesh/#multi-grading Notes ----- * Specify one or two chopping parameters (start/end size, c2c expansion, total expansion, count). That specifies grading completely. Using more than two makes the calculation over-defined and will yield inconsistent results or will throw an exception. * When only one parameter is given, ``c2c_expansion`` defaults to 1 and a uniform cell size is produced. * ``total_expansion`` cannot be used with ``c2c_expansion`` = 1. * ``take`` controls which edge length in given axis is taken when calculating grading.
- `chop_edge(self, corner_1: int, corner_2: int, **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `from_series(faces: list[classy_blocks.construct.flat.face.Face]) -> 'Operation'`: Creates a Loft from a list of faces. At least two are required. From faces in between, side edges are created: - 2 faces: no side edges - 3: Arcs - 4 or more: Splines
- `get_all_faces(self) -> dict[typing.Literal['left', 'right', 'front', 'back', 'top', 'bottom'], classy_blocks.construct.flat.face.Face]`: Returns a list of all faces
- `get_closest_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has a center nearest to given point
- `get_closest_side(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> Literal['left', 'right', 'front', 'back', 'top', 'bottom']`: Returns side (bottom/top/left/right/front/back) of the closest face to given point
- `get_face(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> classy_blocks.construct.flat.face.Face`: Returns a new Face on specified side of the Operation. Warning: bottom, left and front faces must be inverted prior to using them for a loft/extrude etc (they point inside the operation by default).
- `get_index_from_side(side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> int`: Returns index of edges/patches/projections from given orient
- `get_normal_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has normal closest to vector that connects returned face and 'point' (viewer).
- `get_patches_at_corner(self, corner: int) -> set`: Returns patch names at given corner (up to 3)
- `invert(self) -> 'Operation'`: Flips top and bottom face
- `mirror(self, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Mirroring an operation will create an inside-out block but automatic reordering of all vertices would create confusion. To avoid both, bottom and top face are swapped after mirroring so that original and mirrored lofts face the same z-direction.
- `project_corner(self, corner: int, label: Union[str, list[str]]) -> None`: Project the vertex at given corner (local index 0...7) to a single surface or an intersection of multiple surface. WIP according to https://github.com/OpenFOAM/OpenFOAM-10/blob/master/src/meshTools/searchableSurfaces/searchableSurfacesQueries/searchableSurfacesQueries.H
- `project_edge(self, corner_1: int, corner_2: int, label: Union[str, list[str]]) -> None`: Replace an edge between given corners with a Projected one or add geometry to an already projected edge
- `project_side(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom'], label: str, edges: bool = False, points: bool = False) -> None`: Project given side to a labeled geometry; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right'; the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - label: name of predefined geometry (add separately to Mesh object) - edges:if True, all edges belonging to this side will also be projected
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Assign a cellZone to this block.
- `set_patch(self, sides: Union[Literal['left', 'right', 'front', 'back', 'top', 'bottom'], list[Literal['left', 'right', 'front', 'back', 'top', 'bottom']]], name: str) -> None`: Assign a patch to given side of the block; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right', a single value or a list of sides; names correspond to position in the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - name: the name that goes into blockMeshDict Use mesh.set_patch_* methods to change other properties (type and other settings)
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self, transforms)`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `unchop(self, axis: Optional[Literal[0, 1, 2]] = None) -> None`: Removes existing chops from an operation (comes handy after copying etc.)

---

### `class CurveBase`

A parametric/analytic/interpolated curve in 3D space: <point> = f(t)

**Constructor:** `CurveBase()`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `discretize(self, param_from: Optional[float] = None, param_to: Optional[float] = None, count: int = 10) -> NDArray[Shape['*, 3'], Any]`: Discretizes this curve into 'count' points. Optionally, use the curve between passed parameters; default 'count' is chosen as a sane default for a blockMesh edge.
- `get_binormal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns the binormal vector from Frenet-Serret TNB frame (https://en.wikipedia.org/wiki/Frenet%E2%80%93Serret_formulas)
- `get_closest_param(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> float`: Finds the parameter on curve where point is the closest to given point.
- `get_closest_point(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> NDArray[Shape['3, 1'], Any]`
- `get_length(self, param_from: Optional[float] = None, param_to: Optional[float] = None) -> float`: Returns the length of the curve between the given parameters; bounds are used if they are not supplied.
- `get_normal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximated normal vector at given parameter
- `get_param_at_length(self, length: float) -> float`: Returns parameter at specified length along the curve
- `get_point(self, param: float) -> NDArray[Shape['3, 1'], Any]`: Returns point at given parameter
- `get_tangent(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximate, normalized tangent to the curve at given parameter
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class CurveClamp`

Clamp that restricts point movement during optimization
to a predefined curve.

The curve parameter that corresponds to given vertex's position
is obtained automatically by minimization. To provide a better starting
point in case minimization fails or produces wrong results,
an initial parameter can be supplied.

**Constructor:** `CurveClamp(position: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], curve: classy_blocks.construct.curves.curve.CurveBase, initial_param: Optional[float] = None)`


**Methods:**

- `get_params(self) -> list[float]`: Returns parameters from initial vertex position
- `update_params(self, params: list[float])`: Updates parameters to given.

---

### `class Cylinder`

Half of a cylinder; it is constructed from
given point and axis in a positive sense - right-hand rule.

Args:
axis_point_1: position of start face
axis_point_2: position of end face
radius_point_1: defines starting point and radius

**Constructor:** `Cylinder(axis_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], axis_point_2: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `chain(source: classy_blocks.construct.shapes.round.RoundSolidShape, length: float, start_face: bool = False) -> 'Cylinder'`: Creates a new Cylinder on start or end face of a round Shape (Elbow, Frustum, Cylinder); Use length > 0 to extrude 'forward' from source's end face; Use length > 0 and `start_face=True` to extrude 'backward' from source's start face
- `chop(self, axis: Literal[0, 1, 2], **kwargs) -> None`: Chops operations along given axis. Only axis 0 and 1 are allowed as defined in sketch_1
- `chop_axial(self, **kwargs)`: Chop the shape between start and end face
- `chop_radial(self, **kwargs)`: Chop the outer 'ring', or 'shell'; core blocks will be defined by tangential chops
- `chop_tangential(self, **kwargs)`: Circumferential chop; also defines core sizes
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `fill(source: 'ExtrudedRing') -> 'Cylinder'`: Fills the inside of the ring with a matching cylinder
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `remove_inner_edges(self, start: bool = True, end: bool = True) -> None`: Removes spline edges from cylinders. This needs to be done in cases where any of the start/end plane points will move (due to optimization or manual adjustments).
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_end_patch(self, name: str) -> None`: Assign the faces of end sketch to a named patch
- `set_outer_patch(self, name: str) -> None`
- `set_start_patch(self, name: str) -> None`: Assign the faces of start sketch to a named patch
- `set_symmetry_patch(self, _name: str) -> None`
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class DiscreteCurve`

A curve, defined by a set of points;
All operations on this curve involve only the specified
points with no interpolation (contrary to *InterpolatedCurves where
values between points are interpolated).

Parameter is actually an index to a given point;
Discretization yields the original points;
Length just sums the distances between points.

**Constructor:** `DiscreteCurve(points: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]])`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `discretize(self, param_from: Optional[float] = None, param_to: Optional[float] = None, _count: int = 0) -> NDArray[Shape['*, 3'], Any]`: Discretizes this curve into points. With DiscreteCurve, parameter 'count' is ignored as points are taken directly.
- `get_binormal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns the binormal vector from Frenet-Serret TNB frame (https://en.wikipedia.org/wiki/Frenet%E2%80%93Serret_formulas)
- `get_closest_param(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> float`: Returns the index of point on this curve where distance to supplied point is the smallest.
- `get_closest_point(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> NDArray[Shape['3, 1'], Any]`
- `get_length(self, param_from: Optional[float] = None, param_to: Optional[float] = None) -> float`: Returns the length of this curve between specified params.
- `get_normal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximated normal vector at given parameter
- `get_param_at_length(self, length: float) -> float`: Returns parameter at specified length along the curve
- `get_point(self, param: float) -> NDArray[Shape['3, 1'], Any]`: Returns point at given parameter
- `get_tangent(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximate, normalized tangent to the curve at given parameter
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class EighthSphere`

One eighth of a sphere, the base shape everything sphere-related

**Constructor:** `EighthSphere(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], diagonal_angle: float = 0.6283185307179586)`


**Methods:**

- `chop_axial(self, **kwargs)`: Chop along given normal
- `chop_radial(self, **kwargs)`: Chop along radius vector
- `chop_tangential(self, **kwargs)`: Chop circumferentially
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_start_patch(self, name: str) -> None`
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Elbow`

A curved round shape of varying cross-section

**Constructor:** `Elbow(center_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], sweep_angle: float, arc_center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], rotation_axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_2: float)`


**Methods:**

- `chain(source: classy_blocks.construct.shapes.round.RoundSolidShape, sweep_angle: float, arc_center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], rotation_axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_2: float, start_face: bool = False) -> 'Elbow'`: Use another round Shape's end face as a starting point for this Elbow; Returns a new Elbow object. To start from the other side, use start_face = True
- `chop(self, axis: Literal[0, 1, 2], **kwargs) -> None`: Chops operations along given axis. Only axis 0 and 1 are allowed as defined in sketch_1
- `chop_axial(self, **kwargs)`: Chop the shape between start and end face
- `chop_radial(self, **kwargs)`: Chop the outer 'ring', or 'shell'; core blocks will be defined by tangential chops
- `chop_tangential(self, **kwargs)`: Circumferential chop; also defines core sizes
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `remove_inner_edges(self, start: bool = True, end: bool = True) -> None`: Removes spline edges from cylinders. This needs to be done in cases where any of the start/end plane points will move (due to optimization or manual adjustments).
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_end_patch(self, name: str) -> None`: Assign the faces of end sketch to a named patch
- `set_outer_patch(self, name: str) -> None`
- `set_start_patch(self, name: str) -> None`: Assign the faces of start sketch to a named patch
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Extrude`

Takes a Face and extrudes it by 'amount'.
If 'amount' is float, the extrude direction is normal to 'base'.

**Constructor:** `Extrude(base: classy_blocks.construct.flat.face.Face, amount: Union[float, collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `add_side_edge(self, corner_idx: int, edge_data: classy_blocks.construct.edges.EdgeData) -> None`: Add an edge between two vertices at the same corner of the lower and upper face (index and index+4 or vice versa).
- `chop(self, axis: Literal[0, 1, 2], **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`: Chop the whole operation (set cell count and optional grading) in one direction. Parameters ---------- Axis : int Direction in which to apply the chop: * **0** - along the first edge of a face * **1** - along the second edge of a face * **2** - between faces / along the operation path Keyword arguments ---------------- start_size : float, optional Width of the first cell. end_size : float, optional Width of the last cell. count : int, optional Number of cells in the chosen direction. c2c_expansion : float, optional Cell-to-cell expansion ratio (default = 1). total_expansion : float, optional Ratio between the first and last cell size. take : optional Edge length to use when computing the cell count. Use 'min', 'max' or 'avg' (the default) preserve : optional Which parameter to maintain consistent when distributing chops to other blocks in the same row. Can be ``c2c_expansion``, ``start_size`` or ``end_size``. The default is ``total_expansion``. length_ratio : optional To use multi-graded blocks, add multiple chops to the same axis by calling ``.chop()`` multiple times. Each chop takes a fraction of length (should total to 1) which is specified by ``length_ratio``. https://cfd.direct/openfoam/user-guide/v9-blockMesh/#multi-grading Notes ----- * Specify one or two chopping parameters (start/end size, c2c expansion, total expansion, count). That specifies grading completely. Using more than two makes the calculation over-defined and will yield inconsistent results or will throw an exception. * When only one parameter is given, ``c2c_expansion`` defaults to 1 and a uniform cell size is produced. * ``total_expansion`` cannot be used with ``c2c_expansion`` = 1. * ``take`` controls which edge length in given axis is taken when calculating grading.
- `chop_edge(self, corner_1: int, corner_2: int, **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `from_series(faces: list[classy_blocks.construct.flat.face.Face]) -> 'Operation'`: Creates a Loft from a list of faces. At least two are required. From faces in between, side edges are created: - 2 faces: no side edges - 3: Arcs - 4 or more: Splines
- `get_all_faces(self) -> dict[typing.Literal['left', 'right', 'front', 'back', 'top', 'bottom'], classy_blocks.construct.flat.face.Face]`: Returns a list of all faces
- `get_closest_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has a center nearest to given point
- `get_closest_side(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> Literal['left', 'right', 'front', 'back', 'top', 'bottom']`: Returns side (bottom/top/left/right/front/back) of the closest face to given point
- `get_face(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> classy_blocks.construct.flat.face.Face`: Returns a new Face on specified side of the Operation. Warning: bottom, left and front faces must be inverted prior to using them for a loft/extrude etc (they point inside the operation by default).
- `get_index_from_side(side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> int`: Returns index of edges/patches/projections from given orient
- `get_normal_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has normal closest to vector that connects returned face and 'point' (viewer).
- `get_patches_at_corner(self, corner: int) -> set`: Returns patch names at given corner (up to 3)
- `invert(self) -> 'Operation'`: Flips top and bottom face
- `mirror(self, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Mirroring an operation will create an inside-out block but automatic reordering of all vertices would create confusion. To avoid both, bottom and top face are swapped after mirroring so that original and mirrored lofts face the same z-direction.
- `project_corner(self, corner: int, label: Union[str, list[str]]) -> None`: Project the vertex at given corner (local index 0...7) to a single surface or an intersection of multiple surface. WIP according to https://github.com/OpenFOAM/OpenFOAM-10/blob/master/src/meshTools/searchableSurfaces/searchableSurfacesQueries/searchableSurfacesQueries.H
- `project_edge(self, corner_1: int, corner_2: int, label: Union[str, list[str]]) -> None`: Replace an edge between given corners with a Projected one or add geometry to an already projected edge
- `project_side(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom'], label: str, edges: bool = False, points: bool = False) -> None`: Project given side to a labeled geometry; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right'; the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - label: name of predefined geometry (add separately to Mesh object) - edges:if True, all edges belonging to this side will also be projected
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Assign a cellZone to this block.
- `set_patch(self, sides: Union[Literal['left', 'right', 'front', 'back', 'top', 'bottom'], list[Literal['left', 'right', 'front', 'back', 'top', 'bottom']]], name: str) -> None`: Assign a patch to given side of the block; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right', a single value or a list of sides; names correspond to position in the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - name: the name that goes into blockMeshDict Use mesh.set_patch_* methods to change other properties (type and other settings)
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self, transforms)`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `unchop(self, axis: Optional[Literal[0, 1, 2]] = None) -> None`: Removes existing chops from an operation (comes handy after copying etc.)

---

### `class ExtrudedRing`

A ring, created by specifying its base, then extruding it

**Constructor:** `ExtrudedRing(axis_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], axis_point_2: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], outer_radius_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], inner_radius: float, n_segments: int = 8)`


**Methods:**

- `chain(source: 'ExtrudedRing', length: float, start_face: bool = False) -> 'ExtrudedRing'`: Creates a new ExtrudedRing on end face of source ring; use start_face=False to chain 'backwards' from the first face
- `chop(self, axis: Literal[0, 1, 2], **kwargs) -> None`: Chops operations along given axis. Only axis 0 and 1 are allowed as defined in sketch_1
- `chop_axial(self, **kwargs)`: Chop the shape between start and end face
- `chop_radial(self, **kwargs)`: Chop the outer 'ring', or 'shell'
- `chop_tangential(self, **kwargs) -> None`: Circumferential chop
- `contract(source: 'ExtrudedRing', inner_radius: float) -> 'ExtrudedRing'`: Create a new ring on inner surface of the source
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `expand(source: Union[classy_blocks.construct.shapes.round.RoundSolidShape, classy_blocks.construct.shapes.round.RoundHollowShape], thickness: float) -> 'ExtrudedRing'`: Create a new concentric Ring with radius, enlarged by 'thickness'; Can be used on Cylinder or ExtrudedRing
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `remove_inner_edges(self, start: bool = True, end: bool = True) -> None`: Removes spline edges from cylinders. This needs to be done in cases where any of the start/end plane points will move (due to optimization or manual adjustments).
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_end_patch(self, name: str) -> None`: Assign the faces of end sketch to a named patch
- `set_inner_patch(self, name: str) -> None`: Assign the faces of inside surface to a named patch
- `set_outer_patch(self, name: str) -> None`
- `set_start_patch(self, name: str) -> None`: Assign the faces of start sketch to a named patch
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class ExtrudedShape`

Analogous to an Extrude operation but on a Sketch

**Constructor:** `ExtrudedShape(sketch: classy_blocks.construct.flat.sketch.Sketch, amount: Union[float, collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `chop(self, axis: Literal[0, 1, 2], **kwargs) -> None`: Chops operations along given axis. Only axis 0 and 1 are allowed as defined in sketch_1
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_end_patch(self, name: str) -> None`: Assign the faces of end sketch to a named patch
- `set_start_patch(self, name: str) -> None`: Assign the faces of start sketch to a named patch
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class ExtrudedStack`

Extruded shapes, stacked on top of each other.
Amount is overall 'height' of the stack.

**Constructor:** `ExtrudedStack(base: classy_blocks.construct.flat.sketch.Sketch, amount: Union[float, collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], repeats: int)`


**Methods:**

- `chop(self, **kwargs) -> None`: Adds a chop in lofted/extruded/revolved direction to one operation in each shape in the stack.
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `get_slice(self, axis: Literal[0, 1, 2], index: int) -> list[classy_blocks.construct.operations.operation.Operation]`: Returns all operation with given index in specified axis. For cartesian grids this is equivalent to 'lofts on the same plane'; This does not work with custom/mapped sketches that do not conform to a cartesian grid. Example: A stack that consists of 3 shapes, created from a 2x5 grid. - get_slice(0, i) will return 15 operations (5x3, all operations with the same x-coordinate), - get_slice(1, i) will return 6 operations (2x3, all with the same y-coordinate), - get_slice(2, i) will return 10 operations (2x5, all with the same z-coordinate).
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Face`

A collection of 4 Vertices and optionally 4 Edges,
creating an arbitrary quadrangle.

Args:
- points: a list or a numpy array of exactly 4 points in 3d space
- edges: an optional list of data for edge creation;
    if provided, it must be have exactly 4 elements,
    each element a list of data for edge creation; the format is
    the same as passed to Block.add_edge(). Each element of the list
    represents an edge between its corner and the next, for instance:

    edges=[None, Arc([0.4, 1, 1]]), None, None] will create an arc edge between the 1st and the 2nd vertex
    edges=[Project(['terrain']*4) will project all 4 edges
    of this face: 0-1, 1-2, 2-3, 3-0.

**Constructor:** `Face(points: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]], edges: Optional[list[Optional[classy_blocks.construct.edges.EdgeData]]] = None, check_coplanar: bool = False)`


**Methods:**

- `add_edge(self, corner: int, edge_data: Optional[classy_blocks.construct.edges.EdgeData]) -> None`: Replaces an existing edge between corner and (corner+1); use None to delete an edge (replace with a straight line)
- `copy(self) -> 'Face'`: Returns a copy of this Face
- `invert(self) -> 'Face'`: Reverses the order of points in this face.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `project(self, label: str, edges: bool = False, points: bool = False) -> None`: Project this face to given geometry; faces can only be projected to a single surface, therefore provide a single string (contrary to Edge/Vertex where 2 or even 3 surfaces can be intersected and projected to). Use edges=True and points=True as a shortcut to also project face's edges and points to the same geometry. If you want more control (like projecting an edge to an intersection of two surfaces), use face.edges[0] = edges.Project(['label1', 'label2']). Geometry with provided label must be defined separately in Mesh object.
- `project_edge(self, corner: int, label: Union[str, list[str]]) -> None`: Adds a Project edge or add the label to an existing one
- `remove_edges(self, corners: Optional[list[int]] = None) -> None`: Removes edges (replaces with Lines) from given corners (edges <corner>-<corner+1>). If no corners are provided, all are cleared.
- `reorient(self, start_near: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> 'Face'`: Shifts points of this face in circle so that the starting point is closest to given position; the normal is not affected.
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `shift(self, count: int) -> 'Face'`: Shifts points of this face by 'count', changing its starting point
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, points: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Moves points from current position to given

---

### `class FixedCountGrader`

Calculates and distributes user-defined counts/gradings.
Does not add anything to the mesh - throws an exception if non-graded blocks exist.

**Constructor:** `FixedCountGrader(mesh: classy_blocks.mesh.Mesh, count: int = 5)`


**Methods:**

- `grade(self)`

---

### `class FourCoreDisk`

A disk with four quads in the core and 8 in shell;
the most versatile base for round objects.

**Constructor:** `FourCoreDisk(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `add_core_spline_edges(self) -> None`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self)`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class FreeClamp`

Movement restriction for optimization by vertex movement

**Constructor:** `FreeClamp(position: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `get_params(self) -> list[float]`: Returns parameters from initial vertex position
- `get_params_from_vertex(self)`: Returns parameters from initial vertex position
- `update_params(self, params: list[float])`: Updates parameters to given.

---

### `class Frustum`

Creates a cone frustum (truncated cylinder).

Args:
    axis_point_1: position of the starting face and axis start point
    axis_point_2: position of the end face and axis end point
    radius_point_1: defines starting point for blocks
    radius_2: defines end radius; NOT A POINT!

    Sides are straight unless radius_mid is given; in that case a profiled body
    of revolution is created.

**Constructor:** `Frustum(axis_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], axis_point_2: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_2: float, radius_mid: Optional[float] = None)`


**Methods:**

- `chain(source: classy_blocks.construct.shapes.round.RoundSolidShape, length: float, radius_2: float, start_face: bool = False, radius_mid: Optional[float] = None) -> 'Frustum'`: Chain this Frustum to an existing Shape; Use length > 0 to begin on source's end face; Use length > 0 and `start_face=True` to begin on source's start face and go backwards
- `chop(self, axis: Literal[0, 1, 2], **kwargs) -> None`: Chops operations along given axis. Only axis 0 and 1 are allowed as defined in sketch_1
- `chop_axial(self, **kwargs)`: Chop the shape between start and end face
- `chop_radial(self, **kwargs)`: Chop the outer 'ring', or 'shell'; core blocks will be defined by tangential chops
- `chop_tangential(self, **kwargs)`: Circumferential chop; also defines core sizes
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `remove_inner_edges(self, start: bool = True, end: bool = True) -> None`: Removes spline edges from cylinders. This needs to be done in cases where any of the start/end plane points will move (due to optimization or manual adjustments).
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_end_patch(self, name: str) -> None`: Assign the faces of end sketch to a named patch
- `set_outer_patch(self, name: str) -> None`
- `set_start_patch(self, name: str) -> None`: Assign the faces of start sketch to a named patch
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class GeometricFinder`

Find mesh vertices inside a specified geometric shape

**Constructor:** `GeometricFinder(mesh: classy_blocks.mesh.Mesh)`


**Methods:**

- `find_in_box_center(self, center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], size_x: float, size_y: float, size_z: float) -> set[classy_blocks.items.vertex.Vertex]`: Returns vertices that are inside a box, aligned with cartesian coordinate system and defined by its center and width, height and depth.
- `find_in_box_corners(self, corner_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], diagonal_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> set[classy_blocks.items.vertex.Vertex]`: Returns vertices that are inside a box, aligned with cartesian coordinate system and defined by two points on each end of volumetric diagonal.
- `find_in_sphere(self, position: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius: Optional[float] = None) -> set[classy_blocks.items.vertex.Vertex]`: Returns vertices that are inside a sphere of given radius; if that is not given, constants.TOL is taken
- `find_on_plane(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`: Returns vertices that lie on a plane, defined by a point and normal vector.

---

### `class Grid`

A `n x m` array of rectangles;
not here because it's particularly useful but as an example of a cartesian sketch/stack.

Lies in x-y plane and is aligned with cartesian coordinate system by default
but can be rotated arbitrarily just like other entities.

point_1 is 'lower left' and point_2 is upper right.

TODO: make this more general and user-friendly

**Constructor:** `Grid(point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], point_2: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], count_1: int, count_2: int)`


**Methods:**

- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class HalfDisk`

One half of a four-core disk

**Constructor:** `HalfDisk(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `add_core_spline_edges(self) -> None`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self)`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class HalfSplineDisk`

Sketch for Half oval, elliptical and circular shapes

**Constructor:** `HalfSplineDisk(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_1_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_2_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], side_1: float, side_2: float, **kwargs) -> None`


**Methods:**

- `add_core_spline_edges(self) -> None`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self) -> None`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `add_inner_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to inside of ring
- `add_outer_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to outside of sketch
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `correct_disk(self, corner_1_point: NDArray[Shape['3, 1'], Any], corner_2_point: NDArray[Shape['3, 1'], Any])`: Method to convert a circular disk to the elliptical/oval shape defined
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `outer_spline(self, p_radius: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, center: Optional[nptyping.ndarray.NDArray] = None, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `oval_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `remove_core(self)`: Remove core. Used for rings
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Reimplementation of scale to include side_1 and side_2.
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class HalfSplineRing`

Ring based on SplineRound.

**Constructor:** `HalfSplineRing(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_1_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_2_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], side_1: float, side_2: float, width_1: float, width_2: float, **kwargs)`


**Methods:**

- `add_core_spline_edges(self) -> None`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self) -> None`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `add_inner_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to inside of ring
- `add_outer_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to outside of sketch
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `correct_disk(self, corner_1_point: NDArray[Shape['3, 1'], Any], corner_2_point: NDArray[Shape['3, 1'], Any])`: Method to convert a disk to a ring
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `outer_spline(self, p_radius: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, center: Optional[nptyping.ndarray.NDArray] = None, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `oval_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `remove_core(self)`: Remove core. Used for rings
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Reimplementation of scale to include side_1 and side_2.
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class Hemisphere`

One eighth of a sphere, the base shape everything sphere-related

**Constructor:** `Hemisphere(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], diagonal_angle: float = 0.6283185307179586)`


**Methods:**

- `chain(source, start_face=False)`: Chain this sphere to the end face of a round solid shape; use start_face=True to chain to te start face.
- `chop_axial(self, **kwargs)`: Chop along given normal
- `chop_radial(self, **kwargs)`: Chop along radius vector
- `chop_tangential(self, **kwargs)`: Chop circumferentially
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_outer_patch(self, name)`
- `set_start_patch(self, name: str) -> None`
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class InflationGrader`

Parameters for mesh grading for Low-Re cases.
To save on cell count, only a required thickness (inflation layer)
will be covered with thin cells (c2c_expansion in size ratio between them).
Then a bigger expansion ratio will be applied between the last cell of inflation layer
and the first cell of the bulk flow.

Example:
 ________________
|
|                 > bulk size (cell_size=bulk, no expansion)
|________________
|
|________________ > buffer layer (c2c = 2)
|________________
|================ > inflation layer (cell_size=y+, c2c=1.2)
/ / / / / / / / / wall

Args:
    first_cell_size (float): thickness of the first cell near the wall
    c2c_expansion (float): expansion ratio between cells in inflation layer
    bl_thickness_factor (int): thickness of the inflation layer in y+ units (relative to first_cell_size)
    buffer_expansion (float): expansion between cells in buffer layer
    bulk_cell_size (float): size of cells inside the domain

    The grader will take all relevant blocks and choose one to start with - set cell counts
    and other parameters that must stay fixed for all further blocks.
    It will choose the longest/shortest ('max/min') block edge or something in between ('avg').
    The finest grid will be obtained with 'max', the coarsest with 'min'.

**Constructor:** `InflationGrader(mesh: classy_blocks.mesh.Mesh, first_cell_size: float, bulk_cell_size: float, c2c_expansion: float = 1.2, bl_thickness_factor: int = 30, buffer_expansion: float = 2, take: Literal['min', 'max', 'avg'] = 'avg')`


**Methods:**

- `grade(self)`

---

### `class LJoint`

Base class for mesh-building elements and tools
for manipulation thereof.

**Constructor:** `LJoint(start_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `chop_axial(self, **kwargs)`
- `chop_radial(self, **kwargs)`
- `chop_tangential(self, **kwargs)`
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_hole_patch(self, hole: int, patch_name: str) -> None`
- `set_outer_patch(self, patch_name: str) -> None`
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class LineClamp`

Clamp that restricts point movement
during optimization to a line, defined by 2 points;

Parameter 't' goes from 0 at point_1 to <d> at point_2
where <d> is the distance between the two points
(and beyond if different bounds are specified).

**Constructor:** `LineClamp(position: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], point_2: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], bounds: Optional[tuple[float, float]] = None)`


**Methods:**

- `get_params(self) -> list[float]`: Returns parameters from initial vertex position
- `update_params(self, params: list[float])`: Updates parameters to given.

---

### `class LineCurve`

A simple line, defined by 2 points.
Parameter goes from 0 at point_1 to 1 at point_2.

To extend the line  beyond given points, provide custom 'bounds'.

**Constructor:** `LineCurve(point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], point_2: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], bounds: tuple[float, float] = (0, 1))`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `discretize(self, param_from: Optional[float] = None, param_to: Optional[float] = None, count: int = 15) -> NDArray[Shape['*, 3'], Any]`: Discretized the curve into 'count' points.
- `get_binormal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns the binormal vector from Frenet-Serret TNB frame (https://en.wikipedia.org/wiki/Frenet%E2%80%93Serret_formulas)
- `get_closest_param(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> float`: Finds the param on curve where point is the closest to given point
- `get_closest_point(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> NDArray[Shape['3, 1'], Any]`
- `get_length(self, param_from: Optional[float] = None, param_to: Optional[float] = None) -> float`: Returns the length of the curve between the given parameters; bounds are used if they are not supplied.
- `get_normal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximated normal vector at given parameter
- `get_param_at_length(self, length: float) -> float`: Returns parameter at specified length along the curve
- `get_point(self, param: float) -> NDArray[Shape['3, 1'], Any]`: Returns point at given parameter
- `get_tangent(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximate, normalized tangent to the curve at given parameter
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class LinearInterpolatedCurve`

A curve, obtained by interpolation between provided points;
Unlike DiscreteCurve, all values between points are accessible by
providing appropriate parameter.

The parameter is similar to DiscreteCurve's, like an index to
the nearest point but here all non-integer values in between
are available too.

An interpolation function is build from provided points.
Length, discretization, center and other calculated properties
are based on that function rather than specified points.

**Constructor:** `LinearInterpolatedCurve(points: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]], extrapolate: bool = False, equalize: bool = True)`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `discretize(self, param_from: Optional[float] = None, param_to: Optional[float] = None, count: int = 15) -> NDArray[Shape['*, 3'], Any]`: Discretized the curve into 'count' points.
- `get_binormal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns the binormal vector from Frenet-Serret TNB frame (https://en.wikipedia.org/wiki/Frenet%E2%80%93Serret_formulas)
- `get_closest_param(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> float`: Finds the param on curve where point is the closest to given point
- `get_closest_point(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> NDArray[Shape['3, 1'], Any]`
- `get_length(self, param_from: Optional[float] = None, param_to: Optional[float] = None) -> float`: Returns the length of this curve by summing distance between points. The 'count' parameter is ignored as the original points are taken.
- `get_normal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximated normal vector at given parameter
- `get_param_at_length(self, length: float) -> float`: Returns parameter at specified length along the curve
- `get_point(self, param: float) -> NDArray[Shape['3, 1'], Any]`: Returns point at given parameter
- `get_tangent(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximate, normalized tangent to the curve at given parameter
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class LinkBase`

When optimizing a single vertex position,
other vertices can be linked to it so that they move
together with optimized vertex.

**Constructor:** `LinkBase(leader: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], follower: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `transform(self) -> NDArray[Shape['3, 1'], Any]`: Determine the new vertex position according to the type of link
- `update(self) -> None`

---

### `class Loft`

A base class for all single-block operations
(Box, Loft, Revolve, Extrude, Wedge).

**Constructor:** `Loft(bottom_face: classy_blocks.construct.flat.face.Face, top_face: classy_blocks.construct.flat.face.Face)`


**Methods:**

- `add_side_edge(self, corner_idx: int, edge_data: classy_blocks.construct.edges.EdgeData) -> None`: Add an edge between two vertices at the same corner of the lower and upper face (index and index+4 or vice versa).
- `chop(self, axis: Literal[0, 1, 2], **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`: Chop the whole operation (set cell count and optional grading) in one direction. Parameters ---------- Axis : int Direction in which to apply the chop: * **0** - along the first edge of a face * **1** - along the second edge of a face * **2** - between faces / along the operation path Keyword arguments ---------------- start_size : float, optional Width of the first cell. end_size : float, optional Width of the last cell. count : int, optional Number of cells in the chosen direction. c2c_expansion : float, optional Cell-to-cell expansion ratio (default = 1). total_expansion : float, optional Ratio between the first and last cell size. take : optional Edge length to use when computing the cell count. Use 'min', 'max' or 'avg' (the default) preserve : optional Which parameter to maintain consistent when distributing chops to other blocks in the same row. Can be ``c2c_expansion``, ``start_size`` or ``end_size``. The default is ``total_expansion``. length_ratio : optional To use multi-graded blocks, add multiple chops to the same axis by calling ``.chop()`` multiple times. Each chop takes a fraction of length (should total to 1) which is specified by ``length_ratio``. https://cfd.direct/openfoam/user-guide/v9-blockMesh/#multi-grading Notes ----- * Specify one or two chopping parameters (start/end size, c2c expansion, total expansion, count). That specifies grading completely. Using more than two makes the calculation over-defined and will yield inconsistent results or will throw an exception. * When only one parameter is given, ``c2c_expansion`` defaults to 1 and a uniform cell size is produced. * ``total_expansion`` cannot be used with ``c2c_expansion`` = 1. * ``take`` controls which edge length in given axis is taken when calculating grading.
- `chop_edge(self, corner_1: int, corner_2: int, **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `from_series(faces: list[classy_blocks.construct.flat.face.Face]) -> 'Operation'`: Creates a Loft from a list of faces. At least two are required. From faces in between, side edges are created: - 2 faces: no side edges - 3: Arcs - 4 or more: Splines
- `get_all_faces(self) -> dict[typing.Literal['left', 'right', 'front', 'back', 'top', 'bottom'], classy_blocks.construct.flat.face.Face]`: Returns a list of all faces
- `get_closest_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has a center nearest to given point
- `get_closest_side(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> Literal['left', 'right', 'front', 'back', 'top', 'bottom']`: Returns side (bottom/top/left/right/front/back) of the closest face to given point
- `get_face(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> classy_blocks.construct.flat.face.Face`: Returns a new Face on specified side of the Operation. Warning: bottom, left and front faces must be inverted prior to using them for a loft/extrude etc (they point inside the operation by default).
- `get_index_from_side(side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> int`: Returns index of edges/patches/projections from given orient
- `get_normal_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has normal closest to vector that connects returned face and 'point' (viewer).
- `get_patches_at_corner(self, corner: int) -> set`: Returns patch names at given corner (up to 3)
- `invert(self) -> 'Operation'`: Flips top and bottom face
- `mirror(self, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Mirroring an operation will create an inside-out block but automatic reordering of all vertices would create confusion. To avoid both, bottom and top face are swapped after mirroring so that original and mirrored lofts face the same z-direction.
- `project_corner(self, corner: int, label: Union[str, list[str]]) -> None`: Project the vertex at given corner (local index 0...7) to a single surface or an intersection of multiple surface. WIP according to https://github.com/OpenFOAM/OpenFOAM-10/blob/master/src/meshTools/searchableSurfaces/searchableSurfacesQueries/searchableSurfacesQueries.H
- `project_edge(self, corner_1: int, corner_2: int, label: Union[str, list[str]]) -> None`: Replace an edge between given corners with a Projected one or add geometry to an already projected edge
- `project_side(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom'], label: str, edges: bool = False, points: bool = False) -> None`: Project given side to a labeled geometry; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right'; the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - label: name of predefined geometry (add separately to Mesh object) - edges:if True, all edges belonging to this side will also be projected
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Assign a cellZone to this block.
- `set_patch(self, sides: Union[Literal['left', 'right', 'front', 'back', 'top', 'bottom'], list[Literal['left', 'right', 'front', 'back', 'top', 'bottom']]], name: str) -> None`: Assign a patch to given side of the block; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right', a single value or a list of sides; names correspond to position in the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - name: the name that goes into blockMeshDict Use mesh.set_patch_* methods to change other properties (type and other settings)
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self, transforms)`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `unchop(self, axis: Optional[Literal[0, 1, 2]] = None) -> None`: Removes existing chops from an operation (comes handy after copying etc.)

---

### `class LoftedShape`

A Shape, obtained by taking a two and transforming it once
or twice (middle/end cross-section), then making profiled Lofts
from calculated cross-sections (Elbow, Cylinder, Ring, ...

**Constructor:** `LoftedShape(sketch_1: ~SketchT, sketch_2: ~SketchT, sketch_mid: Union[~SketchT, list[~SketchT], NoneType] = None)`


**Methods:**

- `chop(self, axis: Literal[0, 1, 2], **kwargs) -> None`: Chops operations along given axis. Only axis 0 and 1 are allowed as defined in sketch_1
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_end_patch(self, name: str) -> None`: Assign the faces of end sketch to a named patch
- `set_start_patch(self, name: str) -> None`: Assign the faces of start sketch to a named patch
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class MappedSketch`

A sketch that is created from predefined points.
The points are connected to form quads which define Faces.

**Constructor:** `MappedSketch(positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]], quads: list[list[int]])`


**Methods:**

- `add_edges(self) -> None`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class Mesh`

contains blocks, edges and all necessary methods for assembling blockMeshDict

**Constructor:** `Mesh() -> None`


**Methods:**

- `add(self, solid: Union[classy_blocks.construct.operations.operation.Operation, classy_blocks.construct.shape.Shape, classy_blocks.construct.stack.Stack, classy_blocks.construct.assemblies.assembly.Assembly]) -> None`: Add a classy_blocks solid to the mesh (Loft, Shape, Assembly, ...)
- `add_geometry(self, geometry: dict[str, list[str]]) -> None`: Adds named entry in the 'geometry' section of blockMeshDict; 'geometry' is in the form of dictionary {'geometry_name': [list of properties]}; properties are as specified by searchable* class in documentation. See examples/advanced/project for an example.
- `assemble(self, merge_tol: float = 1e-07) -> classy_blocks.assemble.dump.AssembledDump`: Converts classy_blocks entities (operations and shapes) to actual vertices, edges, blocks and other stuff to be inserted into blockMeshDict. After this has been done, the above objects cease to have any function or influence on mesh.
- `backport(self) -> None`: When mesh is assembled, points from depot are converted to vertices and operations are converted to blocks. When vertices are edited (modification/optimization), depot entities remain unchanged. This can cause problems with some edges (Origin, Axis, ...) and future stuff. This method updates depot from blocks, clears all lists and reassembles the mesh as if it was modified from the start.
- `clear(self) -> None`: Undoes the assemble() method; clears created blocks and other lists but leaves added depot items intact
- `delete(self, operation: classy_blocks.construct.operations.operation.Operation) -> None`: Excludes the given operation from any processing; the data remains but it will not contribute to the mesh
- `grade(self) -> None`: Converts chops from operations into gradings on Blocks. Will fail if the mesh has not been assembled yet and will also raise an exception if chops are over- or under-defined. Is called automatically when writing the mesh.
- `merge_patches(self, master: str, slave: str) -> None`: Merges two non-conforming named patches using face merging; https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility#x13-470004.3.2 (breaks the 100% hex-mesh rule)
- `modify_patch(self, name: str, kind: str, settings: Optional[list[str]] = None) -> None`: Fetches a patch named 'patch' and modifies its type and optionally other settings. They are passed on to blockMeshDict as a list of strings as-is, with no additional brain power used
- `set_default_patch(self, name: str, kind: str) -> None`: Adds the 'defaultPatch' entry to the mesh; any non-specified block boundaries will be assigned this patch
- `write(self, output_path: str, debug_path: Optional[str] = None, merge_tol: float = 1e-07) -> None`: Writes a blockMeshDict to specified location. If debug_path is specified, a VTK file is created first where each block is a single cell, to see simplified blocking in case blockMesh fails with an unfriendly error message.

---

### `class MeshOptimizer`

Provides tools for 2D (sketch) or 3D (mesh blocking) optimization

**Constructor:** `MeshOptimizer(mesh: classy_blocks.mesh.Mesh, report: bool = True, merge_tol: float = 1e-07)`


**Methods:**

- `add_clamp(self, clamp: classy_blocks.optimize.clamps.clamp.ClampBase) -> None`: Adds a clamp to optimization. Raises an exception if it already exists
- `add_link(self, link: classy_blocks.optimize.links.LinkBase) -> None`
- `optimize(self, max_iterations: Optional[int] = None, tolerance: Optional[float] = None, method: Optional[Literal['SLSQP', 'L-BFGS-B', 'Nelder-Mead', 'Powell', 'trust-constr']] = None) -> bool`: Move vertices as defined and restrained with Clamps so that better mesh quality is obtained. Within each iteration, all vertices will be moved, starting with the one with the most influence on quality. Lower tolerance values. max_iterations, tolerance (relative) and method enable rough adjustment of optimization; for fine tuning, modify optimizer.config attribute. Returns True is optimization was successful (tolerance reached)
- `relaxation_factor(self, iteration_no: int) -> float`

---

### `class MeshSmoother`

Helper class that provides a standard way to create an ABC using
inheritance.

**Constructor:** `MeshSmoother(mesh: classy_blocks.mesh.Mesh, merge_tol: float = 1e-07)`


**Methods:**

- `backport(self)`: Copy results of smoothing back to the grid
- `fix_indexes(self, indexes: collections.abc.Iterable[int]) -> None`
- `fix_points(self, points: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]])`
- `smooth(self, iterations: int = 5) -> None`

---

### `class Mirror`

Parameters required to mirror an entity around an
arbitrary plane

**Constructor:** `Mirror(normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> None`


**Methods:**


---

### `class NJoint`

Base class for mesh-building elements and tools
for manipulation thereof.

**Constructor:** `NJoint(start_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], branches: int = 4)`


**Methods:**

- `chop_axial(self, **kwargs)`
- `chop_radial(self, **kwargs)`
- `chop_tangential(self, **kwargs)`
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_hole_patch(self, hole: int, patch_name: str) -> None`
- `set_outer_patch(self, patch_name: str) -> None`
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class OnCurve`

An edge, snapped to a parametric curve

**Constructor:** `OnCurve(curve: classy_blocks.construct.curves.curve.CurveBase, n_points: int = 10, representation: Literal['line', 'arc', 'origin', 'angle', 'spline', 'polyLine', 'project', 'curve'] = 'spline')`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `discretize(self, param_from: float, param_to: float) -> NDArray[Shape['*, 3'], Any]`
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class OneCoreDisk`

A disk with a single block in  the center and four blocks around;
see docs/sketches for point numbers and faces/grid indexing.

**Constructor:** `OneCoreDisk(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `add_core_spline_edges(self)`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self)`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class Operation`

A base class for all single-block operations
(Box, Loft, Revolve, Extrude, Wedge).

**Constructor:** `Operation(bottom_face: classy_blocks.construct.flat.face.Face, top_face: classy_blocks.construct.flat.face.Face)`


**Methods:**

- `add_side_edge(self, corner_idx: int, edge_data: classy_blocks.construct.edges.EdgeData) -> None`: Add an edge between two vertices at the same corner of the lower and upper face (index and index+4 or vice versa).
- `chop(self, axis: Literal[0, 1, 2], **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`: Chop the whole operation (set cell count and optional grading) in one direction. Parameters ---------- Axis : int Direction in which to apply the chop: * **0** - along the first edge of a face * **1** - along the second edge of a face * **2** - between faces / along the operation path Keyword arguments ---------------- start_size : float, optional Width of the first cell. end_size : float, optional Width of the last cell. count : int, optional Number of cells in the chosen direction. c2c_expansion : float, optional Cell-to-cell expansion ratio (default = 1). total_expansion : float, optional Ratio between the first and last cell size. take : optional Edge length to use when computing the cell count. Use 'min', 'max' or 'avg' (the default) preserve : optional Which parameter to maintain consistent when distributing chops to other blocks in the same row. Can be ``c2c_expansion``, ``start_size`` or ``end_size``. The default is ``total_expansion``. length_ratio : optional To use multi-graded blocks, add multiple chops to the same axis by calling ``.chop()`` multiple times. Each chop takes a fraction of length (should total to 1) which is specified by ``length_ratio``. https://cfd.direct/openfoam/user-guide/v9-blockMesh/#multi-grading Notes ----- * Specify one or two chopping parameters (start/end size, c2c expansion, total expansion, count). That specifies grading completely. Using more than two makes the calculation over-defined and will yield inconsistent results or will throw an exception. * When only one parameter is given, ``c2c_expansion`` defaults to 1 and a uniform cell size is produced. * ``total_expansion`` cannot be used with ``c2c_expansion`` = 1. * ``take`` controls which edge length in given axis is taken when calculating grading.
- `chop_edge(self, corner_1: int, corner_2: int, **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `from_series(faces: list[classy_blocks.construct.flat.face.Face]) -> 'Operation'`: Creates a Loft from a list of faces. At least two are required. From faces in between, side edges are created: - 2 faces: no side edges - 3: Arcs - 4 or more: Splines
- `get_all_faces(self) -> dict[typing.Literal['left', 'right', 'front', 'back', 'top', 'bottom'], classy_blocks.construct.flat.face.Face]`: Returns a list of all faces
- `get_closest_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has a center nearest to given point
- `get_closest_side(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> Literal['left', 'right', 'front', 'back', 'top', 'bottom']`: Returns side (bottom/top/left/right/front/back) of the closest face to given point
- `get_face(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> classy_blocks.construct.flat.face.Face`: Returns a new Face on specified side of the Operation. Warning: bottom, left and front faces must be inverted prior to using them for a loft/extrude etc (they point inside the operation by default).
- `get_index_from_side(side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> int`: Returns index of edges/patches/projections from given orient
- `get_normal_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has normal closest to vector that connects returned face and 'point' (viewer).
- `get_patches_at_corner(self, corner: int) -> set`: Returns patch names at given corner (up to 3)
- `invert(self) -> 'Operation'`: Flips top and bottom face
- `mirror(self, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Mirroring an operation will create an inside-out block but automatic reordering of all vertices would create confusion. To avoid both, bottom and top face are swapped after mirroring so that original and mirrored lofts face the same z-direction.
- `project_corner(self, corner: int, label: Union[str, list[str]]) -> None`: Project the vertex at given corner (local index 0...7) to a single surface or an intersection of multiple surface. WIP according to https://github.com/OpenFOAM/OpenFOAM-10/blob/master/src/meshTools/searchableSurfaces/searchableSurfacesQueries/searchableSurfacesQueries.H
- `project_edge(self, corner_1: int, corner_2: int, label: Union[str, list[str]]) -> None`: Replace an edge between given corners with a Projected one or add geometry to an already projected edge
- `project_side(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom'], label: str, edges: bool = False, points: bool = False) -> None`: Project given side to a labeled geometry; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right'; the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - label: name of predefined geometry (add separately to Mesh object) - edges:if True, all edges belonging to this side will also be projected
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Assign a cellZone to this block.
- `set_patch(self, sides: Union[Literal['left', 'right', 'front', 'back', 'top', 'bottom'], list[Literal['left', 'right', 'front', 'back', 'top', 'bottom']]], name: str) -> None`: Assign a patch to given side of the block; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right', a single value or a list of sides; names correspond to position in the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - name: the name that goes into blockMeshDict Use mesh.set_patch_* methods to change other properties (type and other settings)
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self, transforms)`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `unchop(self, axis: Optional[Literal[0, 1, 2]] = None) -> None`: Removes existing chops from an operation (comes handy after copying etc.)

---

### `class Origin`

Parameters for an arc edge, alternative ESI-CFD version;
defined with an origin point and optional flatness (default 1)

https://www.openfoam.com/news/main-news/openfoam-v20-12/pre-processing#x3-22000
https://develop.openfoam.com/Development/openfoam/-/blob/master/src/mesh/blockMesh/blockEdges/arcEdge/arcEdge.H

All arc variants are supported by classy_blocks;
however, only the first (classic) one will be written to blockMeshDict for compatibility.
If an edge was specified by 'angle' or 'origin', the definition will be output as a comment
next to that edge definition.

**Constructor:** `Origin(origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], flatness: float = 1)`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Oval`

A sketch that is created from predefined points.
The points are connected to form quads which define Faces.

**Constructor:** `Oval(center_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], center_point_2: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius: float)`


**Methods:**

- `add_core_spline_edges(self) -> None`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self)`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class ParametricSurfaceClamp`

Clamp that restricts point movement
during optimization to a surface, defined by a function:

p = f(u, v);

Function f must take two parameters 'u' and 'v' and return a single point in 3D space.

**Constructor:** `ParametricSurfaceClamp(position: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], function: Callable[[list[float]], nptyping.ndarray.NDArray], bounds: Optional[list[list[float]]] = None, initial_params: Optional[list[float]] = None)`


**Methods:**

- `get_params(self) -> list[float]`: Returns parameters from initial vertex position
- `update_params(self, params: list[float])`: Updates parameters to given.

---

### `class PlaneClamp`

Clamp that restricts point movement
during optimization to an infinite plane, defined by point and normal.

Bounds are not supported.

**Constructor:** `PlaneClamp(position: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `get_params(self) -> list[float]`: Returns parameters from initial vertex position
- `update_params(self, params: list[float])`: Updates parameters to given.

---

### `class PolyLine`

Parameters for a polyLine edge

**Constructor:** `PolyLine(points: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]])`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `discretize(self, param_from: float, param_to: float) -> NDArray[Shape['*, 3'], Any]`
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Project`

Parameters for a 'project' edge

**Constructor:** `Project(label: Union[str, list[str]])`


**Methods:**

- `add_label(self, label: Union[str, list[str]]) -> None`: Projects this edge to another surface
- `check_length(self) -> None`: Raises an exception if there are too many surfaces to project to
- `convert_label(label: Union[str, list[str]]) -> list[str]`: Makes sure label is always a list of strings of length 1 or 2
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class QuarterCylinder`

Quarter of a cylinder; it is constructed from
given point and axis in a positive sense - right-hand rule.

Args:
axis_point_1: position of start face
axis_point_2: position of end face
radius_point_1: defines starting point and radius

**Constructor:** `QuarterCylinder(axis_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], axis_point_2: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `chop(self, axis: Literal[0, 1, 2], **kwargs) -> None`: Chops operations along given axis. Only axis 0 and 1 are allowed as defined in sketch_1
- `chop_axial(self, **kwargs)`: Chop the shape between start and end face
- `chop_radial(self, **kwargs)`: Chop the outer 'ring', or 'shell'; core blocks will be defined by tangential chops
- `chop_tangential(self, **kwargs)`: Circumferential chop; also defines core sizes
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `remove_inner_edges(self, start: bool = True, end: bool = True) -> None`: Removes spline edges from cylinders. This needs to be done in cases where any of the start/end plane points will move (due to optimization or manual adjustments).
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_end_patch(self, name: str) -> None`: Assign the faces of end sketch to a named patch
- `set_outer_patch(self, name: str) -> None`
- `set_start_patch(self, name: str) -> None`: Assign the faces of start sketch to a named patch
- `set_symmetry_patch(self, name: str) -> None`
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class QuarterSphere`

One eighth of a sphere, the base shape everything sphere-related

**Constructor:** `QuarterSphere(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], diagonal_angle: float = 0.6283185307179586)`


**Methods:**

- `chop_axial(self, **kwargs)`: Chop along given normal
- `chop_radial(self, **kwargs)`: Chop along radius vector
- `chop_tangential(self, **kwargs)`: Chop circumferentially
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_start_patch(self, name: str) -> None`
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class QuarterSplineDisk`

Sketch for Quarter oval, elliptical and circular shapes

**Constructor:** `QuarterSplineDisk(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_1_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_2_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], side_1: float, side_2: float, **kwargs) -> None`


**Methods:**

- `add_core_spline_edges(self) -> None`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self) -> None`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `add_inner_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to inside of ring
- `add_outer_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to outside of sketch
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `correct_disk(self, corner_1_point: NDArray[Shape['3, 1'], Any], corner_2_point: NDArray[Shape['3, 1'], Any])`: Method to convert a circular disk to the elliptical/oval shape defined
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `outer_spline(self, p_radius: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, center: Optional[nptyping.ndarray.NDArray] = None, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `oval_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `remove_core(self)`: Remove core. Used for rings
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Reimplementation of scale to include side_1 and side_2.
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class QuarterSplineRing`

Ring based on SplineRound.

**Constructor:** `QuarterSplineRing(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_1_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_2_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], side_1: float, side_2: float, width_1: float, width_2: float, **kwargs)`


**Methods:**

- `add_core_spline_edges(self) -> None`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self) -> None`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `add_inner_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to inside of ring
- `add_outer_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to outside of sketch
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `correct_disk(self, corner_1_point: NDArray[Shape['3, 1'], Any], corner_2_point: NDArray[Shape['3, 1'], Any])`: Method to convert a disk to a ring
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `outer_spline(self, p_radius: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, center: Optional[nptyping.ndarray.NDArray] = None, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `oval_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `remove_core(self)`: Remove core. Used for rings
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Reimplementation of scale to include side_1 and side_2.
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class RadialClamp`

Clamp that restricts point movement during optimization
to a circular trajectory, defined by center, normal and
vertex position at clamp initialization.

Parameter t goes from 0 at initial vertex position to 2*<r>*pi
at the same position all the way around the circle (with radius <r>)

**Constructor:** `RadialClamp(position: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], bounds: Optional[list[float]] = None)`


**Methods:**

- `get_params(self) -> list[float]`: Returns parameters from initial vertex position
- `update_params(self, params: list[float])`: Updates parameters to given.

---

### `class Revolve`

Takes a Face and revolves it by angle around axis;
axis can be translated so that it goes through desired origin.

Angle is given in radians,
revolve is in positive sense (counter-clockwise - right hand rule)

**Constructor:** `Revolve(base: classy_blocks.construct.flat.face.Face, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `add_side_edge(self, corner_idx: int, edge_data: classy_blocks.construct.edges.EdgeData) -> None`: Add an edge between two vertices at the same corner of the lower and upper face (index and index+4 or vice versa).
- `chop(self, axis: Literal[0, 1, 2], **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`: Chop the whole operation (set cell count and optional grading) in one direction. Parameters ---------- Axis : int Direction in which to apply the chop: * **0** - along the first edge of a face * **1** - along the second edge of a face * **2** - between faces / along the operation path Keyword arguments ---------------- start_size : float, optional Width of the first cell. end_size : float, optional Width of the last cell. count : int, optional Number of cells in the chosen direction. c2c_expansion : float, optional Cell-to-cell expansion ratio (default = 1). total_expansion : float, optional Ratio between the first and last cell size. take : optional Edge length to use when computing the cell count. Use 'min', 'max' or 'avg' (the default) preserve : optional Which parameter to maintain consistent when distributing chops to other blocks in the same row. Can be ``c2c_expansion``, ``start_size`` or ``end_size``. The default is ``total_expansion``. length_ratio : optional To use multi-graded blocks, add multiple chops to the same axis by calling ``.chop()`` multiple times. Each chop takes a fraction of length (should total to 1) which is specified by ``length_ratio``. https://cfd.direct/openfoam/user-guide/v9-blockMesh/#multi-grading Notes ----- * Specify one or two chopping parameters (start/end size, c2c expansion, total expansion, count). That specifies grading completely. Using more than two makes the calculation over-defined and will yield inconsistent results or will throw an exception. * When only one parameter is given, ``c2c_expansion`` defaults to 1 and a uniform cell size is produced. * ``total_expansion`` cannot be used with ``c2c_expansion`` = 1. * ``take`` controls which edge length in given axis is taken when calculating grading.
- `chop_edge(self, corner_1: int, corner_2: int, **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `from_series(faces: list[classy_blocks.construct.flat.face.Face]) -> 'Operation'`: Creates a Loft from a list of faces. At least two are required. From faces in between, side edges are created: - 2 faces: no side edges - 3: Arcs - 4 or more: Splines
- `get_all_faces(self) -> dict[typing.Literal['left', 'right', 'front', 'back', 'top', 'bottom'], classy_blocks.construct.flat.face.Face]`: Returns a list of all faces
- `get_closest_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has a center nearest to given point
- `get_closest_side(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> Literal['left', 'right', 'front', 'back', 'top', 'bottom']`: Returns side (bottom/top/left/right/front/back) of the closest face to given point
- `get_face(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> classy_blocks.construct.flat.face.Face`: Returns a new Face on specified side of the Operation. Warning: bottom, left and front faces must be inverted prior to using them for a loft/extrude etc (they point inside the operation by default).
- `get_index_from_side(side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> int`: Returns index of edges/patches/projections from given orient
- `get_normal_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has normal closest to vector that connects returned face and 'point' (viewer).
- `get_patches_at_corner(self, corner: int) -> set`: Returns patch names at given corner (up to 3)
- `invert(self) -> 'Operation'`: Flips top and bottom face
- `mirror(self, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Mirroring an operation will create an inside-out block but automatic reordering of all vertices would create confusion. To avoid both, bottom and top face are swapped after mirroring so that original and mirrored lofts face the same z-direction.
- `project_corner(self, corner: int, label: Union[str, list[str]]) -> None`: Project the vertex at given corner (local index 0...7) to a single surface or an intersection of multiple surface. WIP according to https://github.com/OpenFOAM/OpenFOAM-10/blob/master/src/meshTools/searchableSurfaces/searchableSurfacesQueries/searchableSurfacesQueries.H
- `project_edge(self, corner_1: int, corner_2: int, label: Union[str, list[str]]) -> None`: Replace an edge between given corners with a Projected one or add geometry to an already projected edge
- `project_side(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom'], label: str, edges: bool = False, points: bool = False) -> None`: Project given side to a labeled geometry; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right'; the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - label: name of predefined geometry (add separately to Mesh object) - edges:if True, all edges belonging to this side will also be projected
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Assign a cellZone to this block.
- `set_patch(self, sides: Union[Literal['left', 'right', 'front', 'back', 'top', 'bottom'], list[Literal['left', 'right', 'front', 'back', 'top', 'bottom']]], name: str) -> None`: Assign a patch to given side of the block; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right', a single value or a list of sides; names correspond to position in the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - name: the name that goes into blockMeshDict Use mesh.set_patch_* methods to change other properties (type and other settings)
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self, transforms)`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `unchop(self, axis: Optional[Literal[0, 1, 2]] = None) -> None`: Removes existing chops from an operation (comes handy after copying etc.)

---

### `class RevolvedRing`

A ring specified by its cross-section; can be of arbitrary shape.
Face points must be specified in the following order:
        p3---___
       /        ---p2
      /              \
     p0---------------p1

0---- -- ----- -- ----- -- ----- -- --->> axis

In this case, chop_*() will work as intended, otherwise
the axes will be swapped or blocks will be inverted.

Because of RevolvedRing's arbitrary shape, there is no
'start' or 'end' sketch and .expand()/.contract() methods
are not available.

This shape is useful when building more complex shapes
of revolution (with non-orthogonal blocks)
from known 2d-blocking in cross-section.

**Constructor:** `RevolvedRing(axis_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], axis_point_2: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], cross_section: classy_blocks.construct.flat.face.Face, n_segments: int = 8)`


**Methods:**

- `chain(source: 'ExtrudedRing', length: float, start_face: bool = False) -> 'ExtrudedRing'`: Creates a new ExtrudedRing on end face of source ring; use start_face=False to chain 'backwards' from the first face
- `chop(self, axis: Literal[0, 1, 2], **kwargs) -> None`: Chops operations along given axis. Only axis 0 and 1 are allowed as defined in sketch_1
- `chop_axial(self, **kwargs)`: Chop the shape between start and end face
- `chop_radial(self, **kwargs)`: Chop the outer 'ring', or 'shell'
- `chop_tangential(self, **kwargs) -> None`: Circumferential chop
- `contract(source: 'ExtrudedRing', inner_radius: float) -> 'ExtrudedRing'`: Create a new ring on inner surface of the source
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `expand(source: Union[classy_blocks.construct.shapes.round.RoundSolidShape, classy_blocks.construct.shapes.round.RoundHollowShape], thickness: float) -> 'ExtrudedRing'`: Create a new concentric Ring with radius, enlarged by 'thickness'; Can be used on Cylinder or ExtrudedRing
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `remove_inner_edges(self, start: bool = True, end: bool = True) -> None`: Removes spline edges from cylinders. This needs to be done in cases where any of the start/end plane points will move (due to optimization or manual adjustments).
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_end_patch(self, name: str) -> None`: Assign the faces of end sketch to a named patch
- `set_inner_patch(self, name: str) -> None`: Assign the faces of inside surface to a named patch
- `set_outer_patch(self, name: str) -> None`
- `set_start_patch(self, name: str) -> None`: Assign the faces of start sketch to a named patch
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class RevolvedShape`

A Shape, obtained by taking a two and transforming it once
or twice (middle/end cross-section), then making profiled Lofts
from calculated cross-sections (Elbow, Cylinder, Ring, ...

**Constructor:** `RevolvedShape(sketch: classy_blocks.construct.flat.sketch.Sketch, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `chop(self, axis: Literal[0, 1, 2], **kwargs) -> None`: Chops operations along given axis. Only axis 0 and 1 are allowed as defined in sketch_1
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_end_patch(self, name: str) -> None`: Assign the faces of end sketch to a named patch
- `set_start_patch(self, name: str) -> None`: Assign the faces of start sketch to a named patch
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class RevolvedStack`

Revolved shapes, stacked around the given center.
Angle given is overall and is divided by repeats for each tier.

**Constructor:** `RevolvedStack(base: classy_blocks.construct.flat.sketch.Sketch, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], repeats: int)`


**Methods:**

- `chop(self, **kwargs) -> None`: Adds a chop in lofted/extruded/revolved direction to one operation in each shape in the stack.
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `get_slice(self, axis: Literal[0, 1, 2], index: int) -> list[classy_blocks.construct.operations.operation.Operation]`: Returns all operation with given index in specified axis. For cartesian grids this is equivalent to 'lofts on the same plane'; This does not work with custom/mapped sketches that do not conform to a cartesian grid. Example: A stack that consists of 3 shapes, created from a 2x5 grid. - get_slice(0, i) will return 15 operations (5x3, all operations with the same x-coordinate), - get_slice(1, i) will return 6 operations (2x3, all with the same y-coordinate), - get_slice(2, i) will return 10 operations (2x5, all with the same z-coordinate).
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Rotation`

Parameters required to rotate an entity

**Constructor:** `Rotation(axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> None`


**Methods:**


---

### `class RotationLink`

A link that maintains the same angular displacement
between parent clamp/vertex and the linked one,
around a given axis.

It will only work correctly when leader is rotated
around given axis and origin.

**Constructor:** `RotationLink(leader: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], follower: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `transform(self) -> NDArray[Shape['3, 1'], Any]`: Determine the new vertex position according to the type of link
- `update(self) -> None`

---

### `class RoundSolidFinder`

Find vertices on start/end faces of a round solid shape
(Cylinder, Elbow, Frustum), ...

**Constructor:** `RoundSolidFinder(mesh: classy_blocks.mesh.Mesh, shape: classy_blocks.construct.shapes.round.RoundSolidShape)`


**Methods:**

- `find_core(self, end_face: bool = False) -> set[classy_blocks.items.vertex.Vertex]`: Returns a list of vertices that define inner vertices of a round shape
- `find_shell(self, end_face: bool = False) -> set[classy_blocks.items.vertex.Vertex]`: Returns a list of vertices on the outer edge of the shape. This only includes two of the vertices that define shell blocks!

---

### `class Scaling`

Parameters required to scale an entity

**Constructor:** `Scaling(ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> None`


**Methods:**


---

### `class SemiCylinder`

Half of a cylinder; it is constructed from
given point and axis in a positive sense - right-hand rule.

Args:
axis_point_1: position of start face
axis_point_2: position of end face
radius_point_1: defines starting point and radius

**Constructor:** `SemiCylinder(axis_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], axis_point_2: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point_1: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `chop(self, axis: Literal[0, 1, 2], **kwargs) -> None`: Chops operations along given axis. Only axis 0 and 1 are allowed as defined in sketch_1
- `chop_axial(self, **kwargs)`: Chop the shape between start and end face
- `chop_radial(self, **kwargs)`: Chop the outer 'ring', or 'shell'; core blocks will be defined by tangential chops
- `chop_tangential(self, **kwargs)`: Circumferential chop; also defines core sizes
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `remove_inner_edges(self, start: bool = True, end: bool = True) -> None`: Removes spline edges from cylinders. This needs to be done in cases where any of the start/end plane points will move (due to optimization or manual adjustments).
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_end_patch(self, name: str) -> None`: Assign the faces of end sketch to a named patch
- `set_outer_patch(self, name: str) -> None`
- `set_start_patch(self, name: str) -> None`: Assign the faces of start sketch to a named patch
- `set_symmetry_patch(self, name: str) -> None`
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Shape`

A collection of Operations that form a predefined
parametric shape

**Constructor:** `Shape()`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class ShapeOptimizer`

Provides tools for 2D (sketch) or 3D (mesh blocking) optimization

**Constructor:** `ShapeOptimizer(operations: list[classy_blocks.construct.operations.operation.Operation], report: bool = True, merge_tol: float = 1e-07)`


**Methods:**

- `add_clamp(self, clamp: classy_blocks.optimize.clamps.clamp.ClampBase) -> None`: Adds a clamp to optimization. Raises an exception if it already exists
- `add_link(self, link: classy_blocks.optimize.links.LinkBase) -> None`
- `optimize(self, max_iterations: Optional[int] = None, tolerance: Optional[float] = None, method: Optional[Literal['SLSQP', 'L-BFGS-B', 'Nelder-Mead', 'Powell', 'trust-constr']] = None) -> bool`: Move vertices as defined and restrained with Clamps so that better mesh quality is obtained. Within each iteration, all vertices will be moved, starting with the one with the most influence on quality. Lower tolerance values. max_iterations, tolerance (relative) and method enable rough adjustment of optimization; for fine tuning, modify optimizer.config attribute. Returns True is optimization was successful (tolerance reached)
- `relaxation_factor(self, iteration_no: int) -> float`

---

### `class Shear`

Parameters required for a shear transform

**Constructor:** `Shear(normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> None`


**Methods:**


---

### `class Shell`

A Shape, created by offsetting faces.
It will contain as many Lofts as there are faces;
edges and projections will be dropped.

Points are offset in direction normal to their owner face;
in case multiple faces share the same point,
average normal is taken.

Shell.operations will hold Lofts in the same order as
passed faces. Use axis=2 for chopping in offset direction.

**Constructor:** `Shell(faces: list[classy_blocks.construct.flat.face.Face], amount: float)`


**Methods:**

- `chop(self, **kwargs) -> None`: Chop in offset direction
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Sets cell zone for all blocks in this shape
- `set_outer_patch(self, name: str) -> None`: Sets patch name for faces that have been offset
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class SimpleGrader`

Calculates and distributes user-defined counts/gradings.
Does not add anything to the mesh - throws an exception if non-graded blocks exist.

**Constructor:** `SimpleGrader(mesh: classy_blocks.mesh.Mesh, cell_size: float, take: Literal['min', 'max', 'avg'] = 'avg')`


**Methods:**

- `grade(self)`

---

### `class Sketch`

A collection of Faces that form the basis of a 3D Shape.

**Constructor:** `Sketch()`


**Methods:**

- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class SketchOptimizer`

Provides tools for 2D (sketch) or 3D (mesh blocking) optimization

**Constructor:** `SketchOptimizer(sketch: classy_blocks.construct.flat.sketch.Sketch, report: bool = True, merge_tol: float = 1e-07)`


**Methods:**

- `add_clamp(self, clamp: classy_blocks.optimize.clamps.clamp.ClampBase) -> None`: Adds a clamp to optimization. Raises an exception if it already exists
- `add_link(self, link: classy_blocks.optimize.links.LinkBase) -> None`
- `auto_optimize(self, max_iterations: Optional[int] = None, tolerance: Optional[float] = None, method: Optional[Literal['SLSQP', 'L-BFGS-B', 'Nelder-Mead', 'Powell', 'trust-constr']] = None) -> bool`: Adds a PlaneClamp to all non-boundary points and optimize the sketch. To include boundary points (those that can be moved along a line or a curve), add clamps manually before calling this method.
- `optimize(self, max_iterations: Optional[int] = None, tolerance: Optional[float] = None, method: Optional[Literal['SLSQP', 'L-BFGS-B', 'Nelder-Mead', 'Powell', 'trust-constr']] = None) -> bool`: Move vertices as defined and restrained with Clamps so that better mesh quality is obtained. Within each iteration, all vertices will be moved, starting with the one with the most influence on quality. Lower tolerance values. max_iterations, tolerance (relative) and method enable rough adjustment of optimization; for fine tuning, modify optimizer.config attribute. Returns True is optimization was successful (tolerance reached)
- `relaxation_factor(self, iteration_no: int) -> float`

---

### `class SketchSmoother`

Helper class that provides a standard way to create an ABC using
inheritance.

**Constructor:** `SketchSmoother(sketch: classy_blocks.construct.flat.sketches.mapped.MappedSketch)`


**Methods:**

- `backport(self)`: Copy results of smoothing back to the grid
- `fix_indexes(self, indexes: collections.abc.Iterable[int]) -> None`
- `fix_points(self, points: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]])`
- `smooth(self, iterations: int = 5) -> None`

---

### `class Spline`

Parameters for a spline edge

**Constructor:** `Spline(points: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]])`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `discretize(self, param_from: float, param_to: float) -> NDArray[Shape['*, 3'], Any]`
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class SplineDisk`

Sketch for oval, elliptical and circular shapes

**Constructor:** `SplineDisk(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_1_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_2_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], side_1: float, side_2: float, **kwargs) -> None`


**Methods:**

- `add_core_spline_edges(self) -> None`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self) -> None`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `add_inner_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to inside of ring
- `add_outer_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to outside of sketch
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `correct_disk(self, corner_1_point: NDArray[Shape['3, 1'], Any], corner_2_point: NDArray[Shape['3, 1'], Any])`: Method to convert a circular disk to the elliptical/oval shape defined
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `outer_spline(self, p_radius: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, center: Optional[nptyping.ndarray.NDArray] = None, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `oval_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `remove_core(self)`: Remove core. Used for rings
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Reimplementation of scale to include side_1 and side_2.
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class SplineInterpolatedCurve`

A curve, obtained by interpolation between provided points;
Unlike DiscreteCurve, all values between points are accessible by
providing appropriate parameter.

The parameter is similar to DiscreteCurve's, like an index to
the nearest point but here all non-integer values in between
are available too.

An interpolation function is build from provided points.
Length, discretization, center and other calculated properties
are based on that function rather than specified points.

**Constructor:** `SplineInterpolatedCurve(points: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]], extrapolate: bool = False, equalize: bool = True)`


**Methods:**

- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `discretize(self, param_from: Optional[float] = None, param_to: Optional[float] = None, count: int = 15) -> NDArray[Shape['*, 3'], Any]`: Discretized the curve into 'count' points.
- `get_binormal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns the binormal vector from Frenet-Serret TNB frame (https://en.wikipedia.org/wiki/Frenet%E2%80%93Serret_formulas)
- `get_closest_param(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> float`: Finds the param on curve where point is the closest to given point
- `get_closest_point(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> NDArray[Shape['3, 1'], Any]`
- `get_length(self, param_from: Optional[float] = None, param_to: Optional[float] = None) -> float`: Returns the length of this curve by summing distance between points. The 'count' parameter is ignored as the original points are taken.
- `get_normal(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximated normal vector at given parameter
- `get_param_at_length(self, length: float) -> float`: Returns parameter at specified length along the curve
- `get_point(self, param: float) -> NDArray[Shape['3, 1'], Any]`: Returns point at given parameter
- `get_tangent(self, param: float, delta: float = 1e-07) -> NDArray[Shape['3, 1'], Any]`: Returns an approximate, normalized tangent to the curve at given parameter
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class SplineRing`

Ring based on SplineRound.

**Constructor:** `SplineRing(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_1_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_2_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], side_1: float, side_2: float, width_1: float, width_2: float, **kwargs)`


**Methods:**

- `add_core_spline_edges(self) -> None`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self) -> None`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `add_inner_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to inside of ring
- `add_outer_spline_edges(self, center: Optional[nptyping.ndarray.NDArray] = None) -> None`: Add curved edge as spline to outside of sketch
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `correct_disk(self, corner_1_point: NDArray[Shape['3, 1'], Any], corner_2_point: NDArray[Shape['3, 1'], Any])`: Method to convert a disk to a ring
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `outer_spline(self, p_radius: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, center: Optional[nptyping.ndarray.NDArray] = None, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `oval_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_1: float, side_1: float, radius_2: float, side_2: float, reverse: bool = False) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `remove_core(self)`: Remove core. Used for rings
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Reimplementation of scale to include side_1 and side_2.
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---

### `class SymmetryLink`

A link that mirrors follower over a given plane.

**Constructor:** `SymmetryLink(leader: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], follower: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `transform(self) -> NDArray[Shape['3, 1'], Any]`: Determine the new vertex position according to the type of link
- `update(self) -> None`

---

### `class TJoint`

Base class for mesh-building elements and tools
for manipulation thereof.

**Constructor:** `TJoint(start_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `chop_axial(self, **kwargs)`
- `chop_radial(self, **kwargs)`
- `chop_tangential(self, **kwargs)`
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_hole_patch(self, hole: int, patch_name: str) -> None`
- `set_outer_patch(self, patch_name: str) -> None`
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class TransformedStack`

A stack where each next tier's sketch is transformed according to a list
of transformations, passed to constructor. Arc edges can be created by specifying
a mid_transforms list. The transformations there refer to base sketch - its vertices
will be used as arc points for all lofted edges.

**Constructor:** `TransformedStack(base: classy_blocks.construct.flat.sketch.Sketch, end_transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation], repeats: int, mid_transforms: Optional[collections.abc.Sequence[classy_blocks.base.transforms.Transformation]] = None)`


**Methods:**

- `chop(self, **kwargs) -> None`: Adds a chop in lofted/extruded/revolved direction to one operation in each shape in the stack.
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `get_slice(self, axis: Literal[0, 1, 2], index: int) -> list[classy_blocks.construct.operations.operation.Operation]`: Returns all operation with given index in specified axis. For cartesian grids this is equivalent to 'lofts on the same plane'; This does not work with custom/mapped sketches that do not conform to a cartesian grid. Example: A stack that consists of 3 shapes, created from a 2x5 grid. - get_slice(0, i) will return 15 operations (5x3, all operations with the same x-coordinate), - get_slice(1, i) will return 6 operations (2x3, all with the same y-coordinate), - get_slice(2, i) will return 10 operations (2x5, all with the same z-coordinate).
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.

---

### `class Translation`

Parameters required to translate an entity

**Constructor:** `Translation(displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> None`


**Methods:**


---

### `class TranslationLink`

A link that maintains the same translation vector
between parent clamp/vertex and the linked one.

**Constructor:** `TranslationLink(leader: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], follower: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `transform(self) -> NDArray[Shape['3, 1'], Any]`: Determine the new vertex position according to the type of link
- `update(self) -> None`

---

### `class ViewpointReorienter`

Reorient an Operation so that faces are aligned as viewed by
observer from a specified viewpoint.
Two points must be specified, one 'in front' of the block (preferrably far away)
and other 'above' the block (can also be far away).

Will fail with degenerate hexahedras (concavity, wedges, dubiously aligned faces, ...).

Reorienting will be done in-place so that all other Operation attributes
remain unchanged. Therefore it is recommended you do sorting BEFORE adding
any edges, patches, and so on. In other case, behaviour is undetermined.

**Constructor:** `ViewpointReorienter(observer: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], ceiling: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `reorient(self, operation: classy_blocks.construct.operations.operation.Operation)`

---

### `class Wedge`

Revolves 'face' around x-axis symetrically by +/- angle/2.
By default, the angle is 2 degrees.

Used for creating wedge-type geometries for axisymmetric cases.
Automatically creates wedge patches* (you still
need to include them in changeDictionaryDict - type: wedge).

* - default naming of block sides is not very intuitive
for wedge geometry so additional names are available for wedges:
    set_inner_patch() (= 'front')
    set_outer_patch() (= 'back')
other two patches are wedge_left and wedge_right. Sides are named
according to this sketch:

                    outer
    _________________________________
    |                               |
    | left                    right |
    |_______________________________|
                    inner
__  _____  __  _____  __  _____  __  __ axis of symmetry (x)

**Constructor:** `Wedge(face: classy_blocks.construct.flat.face.Face, angle: Optional[float] = None)`


**Methods:**

- `add_side_edge(self, corner_idx: int, edge_data: classy_blocks.construct.edges.EdgeData) -> None`: Add an edge between two vertices at the same corner of the lower and upper face (index and index+4 or vice versa).
- `chop(self, axis: Literal[0, 1, 2], **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`: Chop the whole operation (set cell count and optional grading) in one direction. Parameters ---------- Axis : int Direction in which to apply the chop: * **0** - along the first edge of a face * **1** - along the second edge of a face * **2** - between faces / along the operation path Keyword arguments ---------------- start_size : float, optional Width of the first cell. end_size : float, optional Width of the last cell. count : int, optional Number of cells in the chosen direction. c2c_expansion : float, optional Cell-to-cell expansion ratio (default = 1). total_expansion : float, optional Ratio between the first and last cell size. take : optional Edge length to use when computing the cell count. Use 'min', 'max' or 'avg' (the default) preserve : optional Which parameter to maintain consistent when distributing chops to other blocks in the same row. Can be ``c2c_expansion``, ``start_size`` or ``end_size``. The default is ``total_expansion``. length_ratio : optional To use multi-graded blocks, add multiple chops to the same axis by calling ``.chop()`` multiple times. Each chop takes a fraction of length (should total to 1) which is specified by ``length_ratio``. https://cfd.direct/openfoam/user-guide/v9-blockMesh/#multi-grading Notes ----- * Specify one or two chopping parameters (start/end size, c2c expansion, total expansion, count). That specifies grading completely. Using more than two makes the calculation over-defined and will yield inconsistent results or will throw an exception. * When only one parameter is given, ``c2c_expansion`` defaults to 1 and a uniform cell size is produced. * ``total_expansion`` cannot be used with ``c2c_expansion`` = 1. * ``take`` controls which edge length in given axis is taken when calculating grading.
- `chop_edge(self, corner_1: int, corner_2: int, **kwargs: Unpack[classy_blocks.cbtyping.ChopArgs]) -> None`
- `copy(self: ~ElementBaseT) -> ~ElementBaseT`: Returns a copy of this object
- `from_series(faces: list[classy_blocks.construct.flat.face.Face]) -> 'Operation'`: Creates a Loft from a list of faces. At least two are required. From faces in between, side edges are created: - 2 faces: no side edges - 3: Arcs - 4 or more: Splines
- `get_all_faces(self) -> dict[typing.Literal['left', 'right', 'front', 'back', 'top', 'bottom'], classy_blocks.construct.flat.face.Face]`: Returns a list of all faces
- `get_closest_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has a center nearest to given point
- `get_closest_side(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> Literal['left', 'right', 'front', 'back', 'top', 'bottom']`: Returns side (bottom/top/left/right/front/back) of the closest face to given point
- `get_face(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> classy_blocks.construct.flat.face.Face`: Returns a new Face on specified side of the Operation. Warning: bottom, left and front faces must be inverted prior to using them for a loft/extrude etc (they point inside the operation by default).
- `get_index_from_side(side: Literal['left', 'right', 'front', 'back', 'top', 'bottom']) -> int`: Returns index of edges/patches/projections from given orient
- `get_normal_face(self, point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> classy_blocks.construct.flat.face.Face`: Returns a Face that has normal closest to vector that connects returned face and 'point' (viewer).
- `get_patches_at_corner(self, corner: int) -> set`: Returns patch names at given corner (up to 3)
- `invert(self) -> 'Operation'`: Flips top and bottom face
- `mirror(self, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None)`: Mirroring an operation will create an inside-out block but automatic reordering of all vertices would create confusion. To avoid both, bottom and top face are swapped after mirroring so that original and mirrored lofts face the same z-direction.
- `project_corner(self, corner: int, label: Union[str, list[str]]) -> None`: Project the vertex at given corner (local index 0...7) to a single surface or an intersection of multiple surface. WIP according to https://github.com/OpenFOAM/OpenFOAM-10/blob/master/src/meshTools/searchableSurfaces/searchableSurfacesQueries/searchableSurfacesQueries.H
- `project_edge(self, corner_1: int, corner_2: int, label: Union[str, list[str]]) -> None`: Replace an edge between given corners with a Projected one or add geometry to an already projected edge
- `project_side(self, side: Literal['left', 'right', 'front', 'back', 'top', 'bottom'], label: str, edges: bool = False, points: bool = False) -> None`: Project given side to a labeled geometry; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right'; the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - label: name of predefined geometry (add separately to Mesh object) - edges:if True, all edges belonging to this side will also be projected
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `set_cell_zone(self, cell_zone: str) -> None`: Assign a cellZone to this block.
- `set_inner_patch(self, name: str) -> None`: Set patch closest to axis of rotation (x)
- `set_outer_patch(self, name: str) -> None`: Set patch away from axis of rotation (x)
- `set_patch(self, sides: Union[Literal['left', 'right', 'front', 'back', 'top', 'bottom'], list[Literal['left', 'right', 'front', 'back', 'top', 'bottom']]], name: str) -> None`: Assign a patch to given side of the block; Args: - side: 'bottom', 'top', 'front', 'back', 'left', 'right', a single value or a list of sides; names correspond to position in the sketch from blockMesh documentation: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility bottom, top: faces from which the Operation was created front: along first edge of a face back: opposite front right: along second edge of a face left: opposite right - name: the name that goes into blockMeshDict Use mesh.set_patch_* methods to change other properties (type and other settings)
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self, transforms)`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `unchop(self, axis: Optional[Literal[0, 1, 2]] = None) -> None`: Removes existing chops from an operation (comes handy after copying etc.)

---

### `class WrappedDisk`

A OneCoreDisk but with four additional blocks surrounding it,
making the sketch a square

**Constructor:** `WrappedDisk(center_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], corner_point: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], radius: float, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray])`


**Methods:**

- `add_core_spline_edges(self) -> None`: Add a spline to the core blocks for an optimized mesh.
- `add_edges(self)`: An optional method that will add edges to faces; use `sketch.faces` property to access them.
- `circular_core_spline(self, p_core_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], p_diagonal_ratio: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], reverse: bool = False, center: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> NDArray[Shape['*, 3'], Any]`: Creates the spline points for the core.
- `copy(self: ~SketchT) -> ~SketchT`: Returns a copy of this sketch
- `merge(self, other: Union[list['MappedSketch'], ForwardRef('MappedSketch')])`: Adds a sketch or list of sketches to itself. New faces and indexes are appended and all duplicate points are removed.
- `mirror(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Mirror around a plane, defined by a normal vector and passing through origin; if origin is not given, [0, 0, 0] is assumed
- `rotate(self: ~ElementBaseT, angle: float, axis: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Rotate by 'angle' around 'axis' going through 'origin'; returns the same instance to enable chaining of transformations.
- `scale(self: ~ElementBaseT, ratio: float, origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray, NoneType] = None) -> ~ElementBaseT`: Scale with respect to given origin; returns the same instance to enable chaining of transformations. If no origin is given, the entity is scaled with respect to its center
- `shear(self: ~ElementBaseT, normal: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], origin: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], direction: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray], angle: float) -> ~ElementBaseT`
- `transform(self: ~ElementBaseT, transforms: collections.abc.Sequence[classy_blocks.base.transforms.Transformation]) -> ~ElementBaseT`
- `translate(self: ~ElementBaseT, displacement: Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]) -> ~ElementBaseT`: Move by displacement vector; returns the same instance to enable chaining of transformations.
- `update(self, positions: Union[nptyping.ndarray.NDArray, collections.abc.Sequence[Union[collections.abc.Sequence[Union[int, float]], nptyping.ndarray.NDArray]], collections.abc.Sequence[nptyping.ndarray.NDArray]]) -> None`: Update faces with updated positions

---
