from __future__ import annotations

import itertools
import numpy

from typing import Tuple, Iterable, List, Generator, Optional

from amulet.api.data_types import (
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
from amulet.utils.matrix import transform_matrix


class SelectionBox:
    """
    A SelectionBox is a box that can represent the entirety of a selection or just a subsection
    of one. This allows for non-rectangular and non-contiguous selections.

    The both the minimum and  maximum coordinate points are inclusive.
    """

    def __init__(self, min_point: BlockCoordinatesAny, max_point: BlockCoordinatesAny):
        box = numpy.array([min_point, max_point]).round().astype(numpy.int)
        self._min_x, self._min_y, self._min_z = numpy.min(box, 0).tolist()
        self._max_x, self._max_y, self._max_z = numpy.max(box, 0).tolist()

    @classmethod
    def create_chunk_box(cls, cx: int, cz: int, sub_chunk_size: int = 16):
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
    def create_sub_chunk_box(cls, cx: int, cy: int, cz: int, sub_chunk_size: int = 16):
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

    def __str__(self):
        return f"({self.min}, {self.max})"

    def __contains__(self, item: CoordinatesAny):
        """Is the block (int) or point (float) location within this box."""
        return (
            self._min_x <= item[0] <= self._max_x
            and self._min_y <= item[1] <= self._max_y
            and self._min_z <= item[2] <= self._max_z
        )

    def __eq__(self, other):
        return self.min == other.min and self.max == other.max

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
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
    def bounds(self) -> Tuple[int, int, int, int, int, int]:
        """The minimum and maximum points of the box."""
        return (
            self._min_x,
            self._min_y,
            self._min_z,
            self._max_x,
            self._max_y,
            self._max_z,
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

    def intersection(self, other: SelectionBox) -> SelectionBox:
        """Get a SelectionBox that represents the region contained within self and other.
        Box may be a zero width box. Use self.intersects to check that it actually intersects.
        """
        return SelectionBox(
            numpy.clip(other.min, self.min, self.max),
            numpy.clip(other.max, self.min, self.max),
        )

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
            (numpy.array(self.bounds).reshape(2, 3) - numpy.array(origin))
            / numpy.array(vector),
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

        return tmin if tmin >= 0 else tmax

    def transform(
        self, scale: FloatTriplet, rotation: FloatTriplet, translation: FloatTriplet
    ) -> List[SelectionBox]:
        """creates a list of new transformed SelectionBox(es)."""
        boxes = []
        # TODO: allow this to support rotations that are not 90 degrees
        min_point, max_point = numpy.matmul(
            transform_matrix(scale, rotation, translation),
            numpy.array([[*self.min, 1], [*self.max, 1]]).T,
        ).T[:, :3]
        boxes.append(SelectionBox(min_point, max_point))

        return boxes
