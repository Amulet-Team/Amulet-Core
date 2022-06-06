from __future__ import annotations

import itertools
import numpy
import math

from typing import Tuple, Iterable, Generator, Optional, Union

from amulet.api.data_types import (
    BlockCoordinates,
    BlockCoordinatesAny,
    CoordinatesAny,
    ChunkCoordinates,
    SubChunkCoordinates,
    FloatTriplet,
    PointCoordinatesAny,
)
from amulet.utils.world_utils import (
    block_coords_to_chunk_coords,
    blocks_slice_to_chunk_slice,
)
from amulet.utils.matrix import (
    transform_matrix,
    displacement_matrix,
)
from .abstract_selection import AbstractBaseSelection
from .. import selection


class SelectionBox(AbstractBaseSelection):
    """
    The SelectionBox class represents a single cuboid selection.

    When combined with :class:`~amulet.api.selection.SelectionGroup` it can represent any arbitrary shape.
    """

    __slots__ = (
        "_min_x",
        "_min_y",
        "_min_z",
        "_max_x",
        "_max_y",
        "_max_z",
        "_point_1",
        "_point_2",
    )

    def __init__(self, point_1: BlockCoordinatesAny, point_2: BlockCoordinatesAny):
        """
        Construct a new SelectionBox instance.

        >>> # a selection box that selects one block.
        >>> box = SelectionBox(
        >>>     (0, 0, 0),
        >>>     (1, 1, 1)
        >>> )

        :param point_1: The first point of the selection.
        :param point_2: The second point of the selection.
        """
        box = numpy.array([point_1, point_2]).round().astype(int)
        p1, p2 = box.tolist()
        self._point_1 = tuple(p1)
        self._point_2 = tuple(p2)
        self._min_x, self._min_y, self._min_z = numpy.min(box, 0).tolist()
        self._max_x, self._max_y, self._max_z = numpy.max(box, 0).tolist()

    @classmethod
    def create_chunk_box(
        cls, cx: int, cz: int, sub_chunk_size: int = 16
    ) -> SelectionBox:
        """
        Get a :class:`SelectionBox` containing the whole of a given chunk.

        >>> box = SelectionBox.create_chunk_box(1, 2)
        SelectionBox((16, -1073741824, 32), (32, 1073741824, 48))

        :param cx: The x coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
        return cls(
            (cx * sub_chunk_size, -(2**30), cz * sub_chunk_size),
            ((cx + 1) * sub_chunk_size, 2**30, (cz + 1) * sub_chunk_size),
        )

    @classmethod
    def create_sub_chunk_box(
        cls, cx: int, cy: int, cz: int, sub_chunk_size: int = 16
    ) -> SelectionBox:
        """
        Get a :class:`SelectionBox` containing the whole of a given sub-chunk.

        >>> SelectionBox.create_sub_chunk_box(1, 0, 2)
        SelectionBox((16, 0, 32), (32, 16, 48))

        :param cx: The x coordinate of the chunk
        :param cy: The y coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
        return cls(
            (cx * sub_chunk_size, cy * sub_chunk_size, cz * sub_chunk_size),
            (
                (cx + 1) * sub_chunk_size,
                (cy + 1) * sub_chunk_size,
                (cz + 1) * sub_chunk_size,
            ),
        )

    def create_moved_box(
        self, offset: BlockCoordinatesAny, subtract=False
    ) -> SelectionBox:
        """
        Create a new :class:`SelectionBox` based on this one with the coordinates moved by the given offset.

        :param offset: The amount to move the box.
        :param subtract: If true will subtract the offset rather than adding.
        :return: The new selection with the given offset.
        """
        offset = numpy.array(offset)
        if subtract:
            offset *= -1
        return SelectionBox(offset + self.min, offset + self.max)

    def chunk_locations(self, sub_chunk_size: int = 16) -> Iterable[ChunkCoordinates]:
        cx_min, cz_min, cx_max, cz_max = block_coords_to_chunk_coords(
            self.min_x,
            self.min_z,
            self.max_x - 1,
            self.max_z - 1,
            sub_chunk_size=sub_chunk_size,
        )
        yield from itertools.product(
            range(cx_min, cx_max + 1), range(cz_min, cz_max + 1)
        )

    def chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterable[Tuple[ChunkCoordinates, SelectionBox]]:
        for cx, cz in self.chunk_locations(sub_chunk_size):
            yield (cx, cz), self.intersection(
                SelectionBox.create_chunk_box(cx, cz, sub_chunk_size)
            )

    def chunk_y_locations(self, sub_chunk_size: int = 16) -> Iterable[int]:
        """
        An iterable of all the sub-chunk y indexes this box intersects.

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
        cy_min, cy_max = block_coords_to_chunk_coords(
            self.min_y, self._max_y - 1, sub_chunk_size=sub_chunk_size
        )
        for cy in range(cy_min, cy_max + 1):
            yield cy

    def sub_chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Iterable[SubChunkCoordinates]:
        for cx, cz in self.chunk_locations(sub_chunk_size):
            for cy in self.chunk_y_locations(sub_chunk_size):
                yield cx, cy, cz

    def chunk_count(self, sub_chunk_size: int = 16) -> int:
        cx_min, cz_min, cx_max, cz_max = block_coords_to_chunk_coords(
            self.min_x,
            self.min_z,
            self.max_x - 1,
            self.max_z - 1,
            sub_chunk_size=sub_chunk_size,
        )
        return (cx_max + 1 - cx_min) * (cz_max + 1 - cz_min)

    def sub_chunk_count(self, sub_chunk_size: int = 16) -> int:
        cy_min, cy_max = block_coords_to_chunk_coords(
            self.min_y,
            self.max_y - 1,
            sub_chunk_size=sub_chunk_size,
        )
        return (cy_max + 1 - cy_min) * self.chunk_count()

    def sub_chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterable[Tuple[SubChunkCoordinates, SelectionBox]]:
        for cx, cy, cz in self.sub_chunk_locations(sub_chunk_size):
            yield (cx, cy, cz), self.intersection(
                SelectionBox.create_sub_chunk_box(cx, cy, cz, sub_chunk_size)
            )

    def __iter__(self) -> Iterable[BlockCoordinates]:
        """An iterable of all the block locations within this box."""
        return self.blocks

    @property
    def blocks(self) -> Iterable[BlockCoordinates]:
        return itertools.product(
            range(self._min_x, self._max_x),
            range(self._min_y, self._max_y),
            range(self._min_z, self._max_z),
        )

    def __repr__(self) -> str:
        return f"SelectionBox({self.point_1}, {self.point_2})"

    def __str__(self) -> str:
        return f"({self.point_1}, {self.point_2})"

    def __contains__(self, item: CoordinatesAny) -> bool:
        return self.contains_block(item)

    def contains_block(self, coords: CoordinatesAny) -> bool:
        return (
            self._min_x <= coords[0] < self._max_x
            and self._min_y <= coords[1] < self._max_y
            and self._min_z <= coords[2] < self._max_z
        )

    def contains_point(self, coords: CoordinatesAny) -> bool:
        return (
            self._min_x <= coords[0] <= self._max_x
            and self._min_y <= coords[1] <= self._max_y
            and self._min_z <= coords[2] <= self._max_z
        )

    def __eq__(self, other) -> bool:
        return self.min == other.min and self.max == other.max

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((*self.min, *self.max))

    @property
    def slice(self) -> Tuple[slice, slice, slice]:
        """
        Converts the :class:`SelectionBox` minimum/maximum coordinates into slice arguments

        :return: The :class:`SelectionBox` coordinates as slices in (x,y,z) order
        """
        return (
            slice(self._min_x, self._max_x),
            slice(self._min_y, self._max_y),
            slice(self._min_z, self._max_z),
        )

    def chunk_slice(
        self, cx: int, cz: int, sub_chunk_size: int = 16
    ) -> Tuple[slice, slice, slice]:
        """
        Get the slice of the box in relative form for a given chunk.

        >>> SelectionBox((0, 0, 0), (32, 32, 32)).chunk_slice(1, 1)
        (slice(0, 16, None), slice(0, 32, None), slice(0, 16, None))

        :param cx: The x coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
        s_x, s_y, s_z = self.slice
        x_chunk_slice = blocks_slice_to_chunk_slice(s_x, sub_chunk_size, cx)
        z_chunk_slice = blocks_slice_to_chunk_slice(s_z, sub_chunk_size, cz)
        return x_chunk_slice, s_y, z_chunk_slice

    def sub_chunk_slice(
        self, cx: int, cy: int, cz: int, sub_chunk_size: int = 16
    ) -> Tuple[slice, slice, slice]:
        """
        Get the slice of the box in relative form for a given sub-chunk.

        >>> SelectionBox((0, 0, 0), (32, 32, 32)).sub_chunk_slice(1, 1, 1)
        (slice(0, 16, None), slice(0, 16, None), slice(0, 16, None))

        :param cx: The x coordinate of the chunk
        :param cy: The y coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
        x_chunk_slice, s_y, z_chunk_slice = self.chunk_slice(cx, cz, sub_chunk_size)
        y_chunk_slice = blocks_slice_to_chunk_slice(s_y, sub_chunk_size, cy)
        return x_chunk_slice, y_chunk_slice, z_chunk_slice

    @property
    def point_1(self) -> BlockCoordinates:
        """The first value given to the constructor."""
        return self._point_1

    @property
    def point_2(self) -> BlockCoordinates:
        """The second value given to the constructor."""
        return self._point_2

    @property
    def points(self) -> Tuple[BlockCoordinates, BlockCoordinates]:
        """The points given to the constructor."""
        return self.point_1, self.point_2

    @property
    def points_array(self) -> numpy.ndarray:
        """The points given to the constructor as a numpy array."""
        return numpy.array(self.points)

    @property
    def min_x(self) -> int:
        return self._min_x

    @property
    def min_y(self) -> int:
        return self._min_y

    @property
    def min_z(self) -> int:
        return self._min_z

    @property
    def max_x(self) -> int:
        return self._max_x

    @property
    def max_y(self) -> int:
        return self._max_y

    @property
    def max_z(self) -> int:
        return self._max_z

    @property
    def min(self) -> BlockCoordinates:
        return self._min_x, self._min_y, self._min_z

    @property
    def min_array(self) -> numpy.ndarray:
        return numpy.array(self.min)

    @property
    def max(self) -> BlockCoordinates:
        return self._max_x, self._max_y, self._max_z

    @property
    def max_array(self) -> numpy.ndarray:
        return numpy.array(self.max)

    @property
    def bounds(self) -> Tuple[BlockCoordinates, BlockCoordinates]:
        return (
            (self._min_x, self._min_y, self._min_z),
            (self._max_x, self._max_y, self._max_z),
        )

    @property
    def bounds_array(self) -> numpy.ndarray:
        return numpy.array(self.bounds)

    @property
    def size_x(self) -> int:
        """The length of the box in the x axis."""
        return self._max_x - self._min_x

    @property
    def size_y(self) -> int:
        """The length of the box in the y axis."""
        return self._max_y - self._min_y

    @property
    def size_z(self) -> int:
        """The length of the box in the z axis."""
        return self._max_z - self._min_z

    @property
    def shape(self) -> Tuple[int, int, int]:
        """
        The shape of the box.

        >>> SelectionBox((0, 0, 0), (1, 1, 1)).shape
        (1, 1, 1)
        """
        return self.size_x, self.size_y, self.size_z

    @property
    def volume(self) -> int:
        """
        The number of blocks in the box.

        >>> SelectionBox((0, 0, 0), (1, 1, 1)).shape
        1
        """
        return self.size_x * self.size_y * self.size_z

    def touches(self, other: SelectionBox) -> bool:
        """
        Method to check if this instance of :class:`SelectionBox` touches but does not intersect another SelectionBox.

        :param other: The other SelectionBox
        :return: True if the two :class:`SelectionBox` instances touch, False otherwise
        """
        # It touches if the box does not intersect but intersects when expanded by one block.
        # There may be a simpler way to do this.
        return self.touches_or_intersects(other) and not self.intersects(other)

    def touches_or_intersects(self, other: SelectionBox) -> bool:
        """
        Method to check if this instance of SelectionBox touches or intersects another SelectionBox.

        :param other: The other SelectionBox.
        :return: True if the two :class:`SelectionBox` instances touch or intersect, False otherwise.
        """
        return not (
            self.min_x >= other.max_x + 1
            or self.min_y >= other.max_y + 1
            or self.min_z >= other.max_z + 1
            or self.max_x <= other.min_x - 1
            or self.max_y <= other.min_y - 1
            or self.max_z <= other.min_z - 1
        )

    def intersects(self, other: SelectionBox) -> bool:
        """
        Method to check whether this instance of SelectionBox intersects another SelectionBox.

        :param other: The other SelectionBox to check for intersection.
        :return: True if the two :class:`SelectionBox` instances intersect, False otherwise.
        """
        return not (
            self.min_x >= other.max_x
            or self.min_y >= other.max_y
            or self.min_z >= other.max_z
            or self.max_x <= other.min_x
            or self.max_y <= other.min_y
            or self.max_z <= other.min_z
        )

    def contains_box(self, other: SelectionBox) -> bool:
        """
        Method to check if the other SelectionBox other fits entirely within this instance of SelectionBox.

        :param other: The SelectionBox to test.
        :return: True if other fits with self, False otherwise.
        """
        return (
            self.min_x <= other.min_x
            and self.min_y <= other.min_y
            and self.min_z <= other.min_z
            and other.max_x <= self.max_x
            and other.max_y <= self.max_y
            and other.max_z <= self.max_z
        )

    def intersection(self, other: SelectionBox) -> SelectionBox:
        return SelectionBox(
            numpy.clip(other.min, self.min, self.max),
            numpy.clip(other.max, self.min, self.max),
        )

    def subtract(self, other: SelectionBox) -> selection.SelectionGroup:
        """
        Get a :class:`~amulet.api.selection.SelectionGroup` containing boxes that are in self but not in other.

        This may be empty if other fully contains self or equal to self if they do not intersect.

        :param other: The SelectionBox to subtract.
        :return:
        """
        if self.intersects(other):
            other = self.intersection(other)
            if self == other:
                # if the two selections are the same there is no difference.
                return selection.SelectionGroup()
            else:
                boxes = []
                if self.min_y < other.min_y:
                    # bottom box
                    boxes.append(
                        SelectionBox(
                            (self.min_x, self.min_y, self.min_z),
                            (self.max_x, other.min_y, self.max_z),
                        )
                    )

                if other.max_y < self.max_y:
                    # top box
                    boxes.append(
                        SelectionBox(
                            (self.min_x, other.max_y, self.min_z),
                            (self.max_x, self.max_y, self.max_z),
                        )
                    )

                # BBB  NNN  TTT
                # BBB  WOE  TTT
                # BBB  SSS  TTT

                if self.min_z < other.min_z:
                    # north box
                    boxes.append(
                        SelectionBox(
                            (self.min_x, other.min_y, self.min_z),
                            (self.max_x, other.max_y, other.min_z),
                        )
                    )

                if other.max_z < self.max_z:
                    # south box
                    boxes.append(
                        SelectionBox(
                            (self.min_x, other.min_y, other.max_z),
                            (self.max_x, other.max_y, self.max_z),
                        )
                    )

                if self.min_x < other.min_x:
                    # west box
                    boxes.append(
                        SelectionBox(
                            (self.min_x, other.min_y, other.min_z),
                            (other.min_x, other.max_y, other.max_z),
                        )
                    )

                if other.max_x < self.max_x:
                    # east box
                    boxes.append(
                        SelectionBox(
                            (other.max_x, other.min_y, other.min_z),
                            (self.max_x, other.max_y, other.max_z),
                        )
                    )

                return selection.SelectionGroup(boxes)
        else:
            # if the boxes do not intersect then the difference is self
            return selection.SelectionGroup(self)

    def intersects_vector(
        self, origin: PointCoordinatesAny, vector: PointCoordinatesAny
    ) -> Optional[float]:
        """
        Determine if a vector from a given point collides with this selection box.

        :param origin: Location of the origin of the vector
        :param vector: The look vector
        :return: Multiplier of the vector to the collision location. None if it does not collide
        """
        # Logic based on https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-box-intersection
        for obj in (origin, vector):
            if isinstance(obj, (tuple, list)):
                if len(obj) != 3 or not all(type(o) in (int, float) for o in obj):
                    raise ValueError(
                        "Given tuple/list type must contain three ints or floats."
                    )
            elif isinstance(obj, numpy.ndarray):
                if obj.shape != (3,) and numpy.issubdtype(obj.dtype, numpy.number):
                    raise ValueError(
                        "Given ndarray type must have a numerical data type with length three."
                    )
        vector = numpy.array(vector)
        vector[abs(vector) < 0.000001] = 0.000001
        (tmin, tymin, tzmin), (tmax, tymax, tzmax) = numpy.sort(
            (self.bounds_array - numpy.array(origin)) / numpy.array(vector), axis=0
        )

        if tmin > tymax or tymin > tmax:
            return None

        if tymin > tmin:
            tmin = tymin

        if tymax < tmax:
            tmax = tymax

        if tmin > tzmax or tzmin > tmax:
            return None

        if tzmin > tmin:
            tmin = tzmin

        if tzmax < tmax:
            tmax = tzmax

        if tmin >= 0:
            return tmin
        elif tmax >= 0:
            return tmax
        else:
            return None

    @staticmethod
    def _transform_points(points: numpy.ndarray, matrix: numpy.ndarray):
        assert (
            isinstance(points, numpy.ndarray)
            and len(points.shape) == 2
            and points.shape[1] == 3
        )
        assert isinstance(matrix, numpy.ndarray) and matrix.shape == (4, 4)
        points_array = numpy.ones((points.shape[0], 4))
        points_array[:, :3] = points
        return numpy.matmul(
            matrix,
            points_array.T,
        ).T[:, :3]

    def _iter_transformed_boxes(
        self, transform: numpy.ndarray
    ) -> Generator[
        Tuple[
            float,  # progress
            SelectionBox,  # The sub-chunk box.
            Union[
                numpy.ndarray,  # The bool array of which of the transformed blocks are contained.
                bool,  # If True all blocks are contained, if False no blocks are contained.
            ],
            Optional[numpy.ndarray],  # A float array of where those blocks came from.
        ],
        None,
        None,
    ]:
        """The core logic for transform and transformed_points"""
        assert isinstance(transform, numpy.ndarray) and transform.shape == (4, 4)
        inverse_transform = numpy.linalg.inv(transform)
        inverse_transform2 = numpy.linalg.inv(
            numpy.matmul(displacement_matrix(-0.5, -0.5, -0.5), transform)
        )

        def transform_box(box_: SelectionBox, transform_) -> SelectionBox:
            """transform a box and get the AABB that contains this rotated box."""

            # find the transformed points of each of the corners
            points = numpy.matmul(
                transform_,
                numpy.array(
                    list(
                        itertools.product(
                            [box_.min_x, box_.max_x],
                            [box_.min_y, box_.max_y],
                            [box_.min_z, box_.max_z],
                            [1],
                        )
                    )
                ).T,
            ).T[:, :3]
            # this is a larger AABB that contains the roatated box and a bit more.
            return SelectionBox(numpy.min(points, axis=0), numpy.max(points, axis=0))

        aabb = transform_box(self, transform)
        count = aabb.sub_chunk_count()
        index = 0

        for _, box in aabb.sub_chunk_boxes():
            index += 1
            original_box = transform_box(box, inverse_transform)
            if self.intersects(original_box):
                # if the boxes do not intersect then nothing needs doing.
                if self.contains_box(original_box):
                    # if the box is fully contained use the whole box.
                    yield index / count, box, True, None
                else:
                    # the original points the transformed locations relate to
                    original_blocks = self._transform_points(
                        numpy.transpose(
                            numpy.mgrid[
                                box.min_x : box.max_x,
                                box.min_y : box.max_y,
                                box.min_z : box.max_z,
                            ],
                            (1, 2, 3, 0),
                        ).reshape(-1, 3),
                        inverse_transform2,
                    )

                    box_shape = box.shape
                    mask: numpy.ndarray = numpy.all(
                        numpy.logical_and(
                            original_blocks < self.max, original_blocks >= self.min
                        ),
                        axis=1,
                    ).reshape(box_shape)

                    yield index / count, box, mask, original_blocks.reshape(
                        box_shape + (3,)
                    )
            else:
                yield index / count, box, False, None

    def transformed_points(
        self, transform: numpy.ndarray
    ) -> Iterable[Tuple[float, Optional[numpy.ndarray], Optional[numpy.ndarray]]]:
        """
        Get the locations of the transformed blocks and the source blocks they came from.

        :param transform: The matrix that this box will be transformed by.
        :return: An iterable of two Nx3 numpy arrays of the source block locations and the destination block locations. The destination locations will be unique but the source may not be and some may not be included.
        """
        for progress, box, mask, original in self._iter_transformed_boxes(transform):
            if isinstance(mask, bool) and mask:
                new_points = numpy.transpose(
                    numpy.mgrid[
                        box.min_x : box.max_x,
                        box.min_y : box.max_y,
                        box.min_z : box.max_z,
                    ],
                    (1, 2, 3, 0),
                ).reshape(-1, 3)
                old_points = self._transform_points(
                    new_points,
                    numpy.linalg.inv(
                        numpy.matmul(displacement_matrix(-0.5, -0.5, -0.5), transform)
                    ),
                )
                yield progress, old_points, new_points
            elif isinstance(mask, numpy.ndarray) and numpy.any(mask):
                yield progress, original[mask], box.min_array + numpy.argwhere(mask)
            else:
                yield progress, None, None

    def transform(
        self, scale: FloatTriplet, rotation: FloatTriplet, translation: FloatTriplet
    ) -> selection.SelectionGroup:
        """
        Creates a :class:`~amulet.api.selection.SelectionGroup` of transformed SelectionBox(es).

        :param scale: A tuple of scaling factors in the x, y and z axis.
        :param rotation: The rotation about the x, y and z axis in radians.
        :param translation: The translation about the x, y and z axis.
        :return: A new :class:`~amulet.api.selection.SelectionGroup` representing the transformed selection.
        """
        quadrant = math.pi / 2
        if all(abs(r - quadrant * round(r / quadrant)) < 0.0001 for r in rotation):
            min_point, max_point = numpy.matmul(
                transform_matrix(scale, rotation, translation),
                numpy.array([[*self.min, 1], [*self.max, 1]]).T,
            ).T[:, :3]
            return selection.SelectionGroup(SelectionBox(min_point, max_point))
        else:
            boxes = []
            for _, box, mask, _ in self._iter_transformed_boxes(
                transform_matrix(scale, rotation, translation)
            ):
                if isinstance(mask, bool):
                    if mask:
                        boxes.append(box)
                else:
                    box_shape = box.shape
                    any_array: numpy.ndarray = numpy.any(mask, axis=2)
                    box_2d_shape = numpy.array(any_array.shape)
                    any_array_flat = any_array.ravel()
                    start_array = numpy.argmax(mask, axis=2)
                    stop_array = box_shape[2] - numpy.argmax(
                        numpy.flip(mask, axis=2), axis=2
                    )
                    # effectively a greedy meshing algorithm in 2D
                    index = 0
                    while index < any_array_flat.size:
                        # while there are unhandled true values
                        index = numpy.argmax(any_array_flat[index:]) + index
                        # find the first true value
                        if any_array_flat[index]:
                            # check that that value is actually True
                            # create the bounds for the box
                            min_x, min_y = max_x, max_y = numpy.unravel_index(
                                index, box_2d_shape
                            )
                            # find the z bounds
                            min_z = start_array[min_x, min_y]
                            max_z = stop_array[min_x, min_y]
                            while max_x < box_2d_shape[0] - 1:
                                # expand in the x while the bounds are the same
                                new_max_x = max_x + 1
                                if (
                                    any_array[new_max_x, max_y]
                                    and start_array[new_max_x, max_y] == min_z
                                    and stop_array[new_max_x, max_y] == max_z
                                ):
                                    # the box z values are the same
                                    max_x = new_max_x
                                else:
                                    break
                            while max_y < box_2d_shape[1] - 1:
                                # expand in the y while the bounds are the same
                                new_max_y = max_y + 1
                                if (
                                    numpy.all(any_array[min_x : max_x + 1, new_max_y])
                                    and numpy.all(
                                        start_array[min_x : max_x + 1, new_max_y]
                                        == min_z
                                    )
                                    and numpy.all(
                                        stop_array[min_x : max_x + 1, new_max_y]
                                        == max_z
                                    )
                                ):
                                    # the box z values are the same
                                    max_y = new_max_y
                                else:
                                    break
                            boxes.append(
                                SelectionBox(
                                    box.min_array + (min_x, min_y, min_z),
                                    box.min_array + (max_x + 1, max_y + 1, max_z),
                                )
                            )
                            any_array[min_x : max_x + 1, min_y : max_y + 1] = False
                        else:
                            # If there are no more True values argmax will return 0
                            break
            return selection.SelectionGroup(boxes)
