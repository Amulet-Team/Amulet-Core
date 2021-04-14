from __future__ import annotations

import itertools
import numpy

from typing import Tuple, Iterable, List, Generator, Optional

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
from amulet.utils.matrix import transform_matrix, inverse_transform_matrix


class SelectionBox:
    """
    A SelectionBox is a box that can represent the entirety of a selection or just a subsection
    of one. This allows for non-rectangular and non-contiguous selections.

    The both the minimum and  maximum coordinate points are inclusive.
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
        """Get a SelectionBox containing the whole of a given chunk.
        :param cx: The x coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        return cls(
            (cx * sub_chunk_size, -(2 ** 30), cz * sub_chunk_size),
            ((cx + 1) * sub_chunk_size, 2 ** 30, (cz + 1) * sub_chunk_size),
        )

    @classmethod
    def create_sub_chunk_box(
        cls, cx: int, cy: int, cz: int, sub_chunk_size: int = 16
    ) -> SelectionBox:
        """Get a SelectionBox containing the whole of a given sub-chunk.
        :param cx: The x coordinate of the chunk
        :param cy: The y coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of the chunk (normally 16)
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
        """Create a new SelectionBox by offsetting the bounds of this box."""
        offset = numpy.array(offset)
        if subtract:
            offset *= -1
        return SelectionBox(offset + self.min, offset + self.max)

    def chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Generator[ChunkCoordinates, None, None]:
        """A generator of chunk locations that this box intersects.
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
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
    ) -> Generator[Tuple[ChunkCoordinates, SelectionBox]]:
        """A generator of modified `SelectionBox`es to fit within each chunk.
        If this box straddles multiple chunks this method will split it up into a box
        for each chunk it intersects along with the chunk coordinates of that chunk.
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        for cx, cz in self.chunk_locations(sub_chunk_size):
            yield (cx, cz), self.intersection(
                SelectionBox.create_chunk_box(cx, cz, sub_chunk_size)
            )

    def chunk_y_locations(self, sub_chunk_size: int = 16) -> Generator[int, None, None]:
        """A generator of all the sub-chunk y indexes this box intersects.
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        cy_min, cy_max = block_coords_to_chunk_coords(
            self.min_y, self._max_y - 1, sub_chunk_size=sub_chunk_size
        )
        for cy in range(cy_min, cy_max + 1):
            yield cy

    def sub_chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Generator[SubChunkCoordinates, None, None]:
        """A generator of all the sub-chunk cx, cy and cz values that this box intersects.
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        for cx, cz in self.chunk_locations(sub_chunk_size):
            for cy in self.chunk_y_locations(sub_chunk_size):
                yield cx, cy, cz

    def sub_chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Generator[Tuple[SubChunkCoordinates, SelectionBox], None, None]:
        """A generator of modified `SelectionBox`es to fit within each sub-chunk.
        If this box straddles multiple sub-chunks this method will split it up into a box
        for each sub-chunk it intersects along with the chunk coordinates of that chunk.
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        for cx, cy, cz in self.sub_chunk_locations(sub_chunk_size):
            yield (cx, cy, cz), self.intersection(
                SelectionBox.create_sub_chunk_box(cx, cy, cz, sub_chunk_size)
            )

    def __iter__(self) -> Iterable[Tuple[int, int, int]]:
        """An iterable of all the block locations within this box."""
        return self.blocks()

    def blocks(self) -> Iterable[Tuple[int, int, int]]:
        """An iterable of all the block locations within this box."""
        return itertools.product(
            range(self._min_x, self._max_x),
            range(self._min_y, self._max_y),
            range(self._min_z, self._max_z),
        )

    def __repr__(self):
        return f"SelectionBox({self.point_1}, {self.point_2})"

    def __str__(self) -> str:
        return f"({self.point_1}, {self.point_2})"

    def __contains__(self, item: CoordinatesAny) -> bool:
        """Is the block (int) or point (float) location within this box."""
        return self.contains_block(item)

    def contains_block(self, coords: CoordinatesAny) -> bool:
        """Is the coordinate greater than or equal to the min point but less than the max point."""
        return (
            self._min_x <= coords[0] < self._max_x
            and self._min_y <= coords[1] < self._max_y
            and self._min_z <= coords[2] < self._max_z
        )

    def contains_point(self, coords: CoordinatesAny) -> bool:
        """Is the coordinate greater than or equal to the min point but less than or equal to the max point."""
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
        Converts the `SelectionBox`es minimum/maximum coordinates into slice arguments

        :return: The `SelectionBox`es coordinates as slices in (x,y,z) order
        """
        return (
            slice(self._min_x, self._max_x),
            slice(self._min_y, self._max_y),
            slice(self._min_z, self._max_z),
        )

    def chunk_slice(
        self, cx: int, cz: int, sub_chunk_size: int = 16
    ) -> Tuple[slice, slice, slice]:
        """Get the slice of the box in relative form for a given chunk.
        eg. SelectionBox((0, 0, 0), (32, 32, 32)).chunk_slice(1, 1) will return
        (slice(0, 16, None), slice(0, 32, None), slice(0, 16, None))
        :param cx: The x coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        s_x, s_y, s_z = self.slice
        x_chunk_slice = blocks_slice_to_chunk_slice(s_x, sub_chunk_size, cx)
        z_chunk_slice = blocks_slice_to_chunk_slice(s_z, sub_chunk_size, cz)
        return x_chunk_slice, s_y, z_chunk_slice

    def sub_chunk_slice(
        self, cx: int, cy: int, cz: int, sub_chunk_size: int = 16
    ) -> Tuple[slice, slice, slice]:
        """Get the slice of the box in relative form for a given sub-chunk.
        eg. SelectionBox((0, 0, 0), (32, 32, 32)).sub_chunk_slice(1, 1, 1) will return
        (slice(0, 16, None), slice(0, 16, None), slice(0, 16, None))
        :param cx: The x coordinate of the chunk
        :param cy: The y coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        x_chunk_slice, s_y, z_chunk_slice = self.chunk_slice(cx, cz, sub_chunk_size)
        y_chunk_slice = blocks_slice_to_chunk_slice(s_y, sub_chunk_size, cy)
        return x_chunk_slice, y_chunk_slice, z_chunk_slice

    @property
    def point_1(self) -> BlockCoordinates:
        return self._point_1

    @property
    def point_2(self) -> BlockCoordinates:
        return self._point_2

    @property
    def points(self) -> Tuple[BlockCoordinates, BlockCoordinates]:
        return self.point_1, self.point_2

    @property
    def points_array(self) -> numpy.ndarray:
        return numpy.array(self.points)

    @property
    def min_x(self) -> int:
        """The minimum x coordinate."""
        return self._min_x

    @property
    def min_y(self) -> int:
        """The minimum y coordinate."""
        return self._min_y

    @property
    def min_z(self) -> int:
        """The minimum z coordinate."""
        return self._min_z

    @property
    def max_x(self) -> int:
        """The maximum x coordinate."""
        return self._max_x

    @property
    def max_y(self) -> int:
        """The maximum y coordinate."""
        return self._max_y

    @property
    def max_z(self) -> int:
        """The maximum z coordinate."""
        return self._max_z

    @property
    def min(self) -> Tuple[int, int, int]:
        """The minimum point of the box."""
        return self._min_x, self._min_y, self._min_z

    @property
    def min_array(self) -> numpy.ndarray:
        """The minimum point of the box as a numpy array."""
        return numpy.array(self.min)

    @property
    def max(self) -> Tuple[int, int, int]:
        """The maximum point of the box."""
        return self._max_x, self._max_y, self._max_z

    @property
    def max_array(self) -> numpy.ndarray:
        """The maximum point of the box as a numpy array."""
        return numpy.array(self.max)

    @property
    def bounds(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """The minimum and maximum points of the box."""
        return (
            (self._min_x, self._min_y, self._min_z),
            (self._max_x, self._max_y, self._max_z),
        )

    @property
    def bounds_array(self) -> numpy.ndarray:
        """The minimum and maximum points of the box as a numpy array."""
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
        """The shape of the box."""
        return self.size_x, self.size_y, self.size_z

    @property
    def volume(self) -> int:
        """The number of blocks in the box."""
        return self.size_x * self.size_y * self.size_z

    def touches(self, other: SelectionBox) -> bool:
        """Method to check if this instance of SelectionBox touches but does not intersect another SelectionBox

        :param other: The other SelectionBox
        :return: True if the two `SelectionBox`es touch, False otherwise
        """
        # It touches if the box does not intersect but intersects when expanded by one block.
        # There may be a simpler way to do this.
        return self.touches_or_intersects(other) and not self.intersects(other)

    def touches_or_intersects(self, other: SelectionBox) -> bool:
        """Method to check if this instance of SelectionBox touches or intersects another SelectionBox

        :param other: The other SelectionBox
        :return: True if the two `SelectionBox`es touch or intersect., False otherwise
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
        Method to check whether this instance of SelectionBox intersects another SelectionBox

        :param other: The other SelectionBox to check for intersection
        :return: True if the two `SelectionBox`es intersect, False otherwise
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
        """Method to check if the other SelectionBox other fits entirely within this instance of SelectionBox.

        :param other: The SelectionBox to test.
        :return: True if other fits with self, False otherwise
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
        """Get a SelectionBox that represents the region contained within self and other.
        Box may be a zero width box. Use self.intersects to check that it actually intersects.
        """
        return SelectionBox(
            numpy.clip(other.min, self.min, self.max),
            numpy.clip(other.max, self.min, self.max),
        )

    def subtract(self, other: SelectionBox) -> List[SelectionBox]:
        """Get a list of `SelectionBox`es that are in self but not in other.
        This may be empty or equal to self."""
        if self.intersects(other):
            other = self.intersection(other)
            if self == other:
                # if the two selections are the same there is no difference.
                return []
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

                return boxes
        else:
            # if the boxes do not intersect then the difference is self
            return [self]

    def intersects_vector(
        self, origin: PointCoordinatesAny, vector: PointCoordinatesAny
    ) -> Optional[float]:
        """
        Determine if a look vector from a given point collides with this selection box.
        :param origin: Location of the origin of the vector
        :param vector: The look vector
        :return: Multiplier of the vector to the collision location. None if it does not collide
        """
        # Logic based on https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-box-intersection
        for obj in (origin, vector):
            if type(obj) in (tuple, list):
                if len(obj) != 3 or not all(type(o) in (int, float) for o in obj):
                    raise ValueError(
                        "Given tuple/list type must contain three ints or floats."
                    )
            elif type(obj) is numpy.ndarray:
                if obj.shape != (3,) and numpy.issubdtype(obj.dtype, numpy.number):
                    raise ValueError(
                        "Given ndarray type must have a numerical data type with length three."
                    )
        vector = numpy.array(vector)
        vector[abs(vector) < 0.000001] = 0.000001
        (tmin, tymin, tzmin), (tmax, tymax, tzmax) = numpy.sort(
            (self.bounds_array - numpy.array(origin)) / numpy.array(vector),
            axis=0,
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

    def transform(
        self, scale: FloatTriplet, rotation: FloatTriplet, translation: FloatTriplet
    ) -> List[SelectionBox]:
        """creates a list of new transformed SelectionBox(es).
        :param scale: A tuple of scaling factors in the x, y and z axis.
        :param rotation: The rotation about the x, y and z axis in radians.
        :param translation: The translation about the x, y and z axis.
        :return:
        """
        boxes = []
        if all(r % 90 == 0 for r in rotation):
            min_point, max_point = numpy.matmul(
                transform_matrix(scale, rotation, translation),
                numpy.array([[*self.min, 1], [*self.max, 1]]).T,
            ).T[:, :3]
            boxes.append(SelectionBox(min_point, max_point))
        else:
            # TODO: Find a way to do this a lot better
            # this could be done better by finding the maximum and minimum y values of the transformed box
            # at each location and reconstructing the box with column boxes.
            transform = transform_matrix(scale, rotation, translation)
            inverse_transform = inverse_transform_matrix(scale, rotation, translation)
            tx, ty, tz = translation
            inverse_transform2 = inverse_transform_matrix(
                scale, rotation, (tx - 0.5, ty - 0.5, tz - 0.5)
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
                return SelectionBox(
                    numpy.min(points, axis=0), numpy.max(points, axis=0)
                )

            aabb = transform_box(self, transform)

            for _, box in aabb.sub_chunk_boxes():
                original_box = transform_box(box, inverse_transform)
                if self.intersects(original_box):
                    # if the boxes do not intersect then nothing needs doing.
                    if self.contains_box(original_box):
                        # if the box is fully contained use the whole box.
                        boxes.append(box)
                    else:
                        # do it block by block
                        # the location of every block in the larger AABB
                        transformed_blocks = list(
                            box.blocks()
                        )

                        # the above in an array form
                        transformed_points = numpy.ones((len(transformed_blocks), 4))
                        transformed_points[:, :3] = transformed_blocks

                        # the original points the transformed locations relate to

                        original_blocks = numpy.matmul(
                            inverse_transform2,
                            transformed_points.T,
                        ).T[:, :3]

                        box_shape = box.shape
                        mask = numpy.all(
                            numpy.logical_and(
                                original_blocks < self.max, original_blocks >= self.min
                            ),
                            axis=1,
                        ).reshape(box_shape)

                        any_array = numpy.any(mask, axis=2)
                        start_array = numpy.argmax(mask, axis=2)
                        stop_array = mask.shape[2] - numpy.argmax(numpy.flip(mask, axis=2), axis=2)
                        for x, y in numpy.argwhere(any_array):
                            min_z = start_array[x, y]
                            if min_z != -1:
                                max_z = stop_array[x, y]
                                boxes.append(
                                    SelectionBox(box.min_array + (x, y, min_z), box.min_array + (x + 1, y + 1, max_z))
                                )

        return boxes
