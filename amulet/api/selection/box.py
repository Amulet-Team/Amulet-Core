from __future__ import annotations

import itertools
import numpy

from typing import Tuple, Iterable, List, Generator

from amulet.api.data_types import (
    BlockCoordinatesAny,
    CoordinatesAny,
    ChunkCoordinates,
    SubChunkCoordinates,
    FloatTriplet,
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
        """Get a SelectionBox containing the whole of a given chunk"""
        return cls(
            (cx * sub_chunk_size, -(2 ** 30), cz * sub_chunk_size),
            ((cx + 1) * sub_chunk_size, 2 ** 30, (cz + 1) * sub_chunk_size),
        )

    @classmethod
    def create_sub_chunk_box(cls, cx: int, cy: int, cz: int, sub_chunk_size: int = 16):
        """Get a SelectionBox containing the whole of a given sub-chunk"""
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
        """A generator of chunk locations that this box intersects."""
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

    def chunk_y_locations(self, sub_chunk_size: int = 16):
        cy_min, cy_max = block_coords_to_chunk_coords(
            self.min_y, self._max_y, sub_chunk_size=sub_chunk_size
        )
        for cy in range(cy_min, cy_max + 1):
            yield cy

    def sub_chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Generator[SubChunkCoordinates, None, None]:
        for cx, cz in self.chunk_locations(sub_chunk_size):
            for cy in self.chunk_y_locations(sub_chunk_size):
                yield cx, cy, cz

    def sub_sections(
        self, sub_chunk_size: int = 16
    ) -> Generator[Tuple[ChunkCoordinates, SelectionBox], None, None]:
        """A generator of modified `SelectionBox`es to fit within each sub-chunk.
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        for cx, cy, cz in self.sub_chunk_locations(sub_chunk_size):
            yield (cx, cz), self.intersection(
                SelectionBox.create_sub_chunk_box(cx, cy, cz, sub_chunk_size)
            )

    def __iter__(self) -> Iterable[Tuple[int, int, int]]:
        return self.blocks()

    def blocks(self) -> Iterable[Tuple[int, int, int]]:
        return itertools.product(
            range(self._min_x, self._max_x),
            range(self._min_y, self._max_y),
            range(self._min_z, self._max_z),
        )

    def __str__(self):
        return f"({self.min}, {self.max})"

    def __contains__(self, item: CoordinatesAny):
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
        """Get the Convert a slice in absolute coordinates to chunk coordinates"""
        s_x, s_y, s_z = self.slice
        x_chunk_slice = blocks_slice_to_chunk_slice(s_x, sub_chunk_size, cx)
        z_chunk_slice = blocks_slice_to_chunk_slice(s_z, sub_chunk_size, cz)
        return x_chunk_slice, s_y, z_chunk_slice

    @property
    def min_x(self) -> int:
        """The minimum x coordinate"""
        return self._min_x

    @property
    def min_y(self) -> int:
        """The minimum y coordinate"""
        return self._min_y

    @property
    def min_z(self) -> int:
        """The minimum z coordinate"""
        return self._min_z

    @property
    def max_x(self) -> int:
        """The maximum x coordinate"""
        return self._max_x

    @property
    def max_y(self) -> int:
        """The maximum y coordinate"""
        return self._max_y

    @property
    def max_z(self) -> int:
        """The maximum z coordinate"""
        return self._max_z

    @property
    def min(self) -> Tuple[int, int, int]:
        """The minimum point of the box"""
        return self._min_x, self._min_y, self._min_z

    @property
    def max(self) -> Tuple[int, int, int]:
        """The maximum point of the box"""
        return self._max_x, self._max_y, self._max_z

    @property
    def bounds(self) -> Tuple[int, int, int, int, int, int]:
        return (
            self._min_x,
            self._min_y,
            self._min_z,
            self._max_x,
            self._max_y,
            self._max_z,
        )

    @property
    def size_x(self) -> int:
        """The length of the box in the x axis"""
        return self._max_x - self._min_x

    @property
    def size_y(self) -> int:
        """The length of the box in the y axis"""
        return self._max_y - self._min_y

    @property
    def size_z(self) -> int:
        """The length of the box in the z axis"""
        return self._max_z - self._min_z

    @property
    def shape(self) -> Tuple[int, int, int]:
        """The shape of the box"""
        return self.size_x, self.size_y, self.size_z

    @property
    def volume(self) -> int:
        return self.size_x * self.size_y * self.size_z

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
        Box may be a zero width box. Use self.intersects to check that it actually intersects."""
        return SelectionBox(
            numpy.clip(other.min, self.min, self.max),
            numpy.clip(other.max, self.min, self.max),
        )

    def transform(
        self, scale: FloatTriplet, rotation: FloatTriplet
    ) -> List[SelectionBox]:
        """creates a list of new transformed SelectionBox(es)."""
        boxes = []
        # TODO: allow this to support rotations that are not 90 degrees
        min_point, max_point = numpy.matmul(
            transform_matrix((0, 0, 0), scale, rotation, "zyx"),
            numpy.array([[*self.min, 1], [*self.max, 1]]).T,
        ).T[:, :3]
        boxes.append(SelectionBox(min_point, max_point))

        return boxes
