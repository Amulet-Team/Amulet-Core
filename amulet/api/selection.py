from __future__ import annotations

import itertools
import numpy

from typing import Tuple, Iterable, List, Generator, Dict

from amulet.api.data_types import (
    BlockCoordinatesAny,
    CoordinatesAny,
    ChunkCoordinates,
    SubChunkCoordinates,
    FloatTriplet,
)
from ..utils.world_utils import (
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
    def create_chunk_box(cls, cx: int, cz: int, chunk_size: int = 16):
        """Get a SelectionBox containing the whole of a given chunk"""
        return cls(
            (cx * chunk_size, -(2 ** 30), cz * chunk_size),
            ((cx + 1) * chunk_size, 2 ** 30, (cz + 1) * chunk_size),
        )

    @classmethod
    def create_sub_chunk_box(cls, cx: int, cy: int, cz: int, chunk_size: int = 16):
        """Get a SelectionBox containing the whole of a given sub-chunk"""
        return cls(
            (cx * chunk_size, cy * chunk_size, cz * chunk_size),
            ((cx + 1) * chunk_size, (cy + 1) * chunk_size, (cz + 1) * chunk_size),
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
        self, chunk_size: int = 16
    ) -> Generator[ChunkCoordinates, None, None]:
        """A generator of chunk locations that this box intersects."""
        cx_min, cz_min, cx_max, cz_max = block_coords_to_chunk_coords(
            self.min_x,
            self.min_z,
            self.max_x - 1,
            self.max_z - 1,
            chunk_size=chunk_size,
        )
        yield from itertools.product(
            range(cx_min, cx_max + 1), range(cz_min, cz_max + 1)
        )

    def chunk_y_locations(self, chunk_size: int = 16):
        cy_min, cy_max = block_coords_to_chunk_coords(
            self.min_y, self._max_y, chunk_size=chunk_size
        )
        for cy in range(cy_min, cy_max + 1):
            yield cy

    def sub_chunk_locations(
        self, chunk_size: int = 16
    ) -> Generator[SubChunkCoordinates, None, None]:
        for cx, cz in self.chunk_locations(chunk_size):
            for cy in self.chunk_y_locations(chunk_size):
                yield cx, cy, cz

    def sub_sections(
        self, chunk_size: int = 16
    ) -> Generator[Tuple[ChunkCoordinates, SelectionBox], None, None]:
        """A generator of modified `SelectionBox`es to fit within each sub-chunk.
        :param chunk_size: The dimension of the chunk (normally 16)
        """
        for cx, cy, cz in self.sub_chunk_locations(chunk_size):
            yield (cx, cz), self.intersection(
                SelectionBox.create_sub_chunk_box(cx, cy, cz, chunk_size)
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
        Converts the SubSelectionBoxes minimum/maximum coordinates into slice arguments

        :return: The SubSelectionBoxes coordinates as slices in (x,y,z) order
        """
        return (
            slice(self._min_x, self._max_x),
            slice(self._min_y, self._max_y),
            slice(self._min_z, self._max_z),
        )

    def chunk_slice(
        self, cx: int, cz: int, chunk_size: int = 16
    ) -> Tuple[slice, slice, slice]:
        """Get the Convert a slice in absolute coordinates to chunk coordinates"""
        s_x, s_y, s_z = self.slice
        x_chunk_slice = blocks_slice_to_chunk_slice(s_x, chunk_size, cx)
        z_chunk_slice = blocks_slice_to_chunk_slice(s_z, chunk_size, cz)
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
        :return: True if the two SubSelectionBoxes intersect, False otherwise
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


class SelectionGroup:
    """
    Holding class for multiple SubSelectionBoxes which allows for non-rectangular and non-contiguous selections
    """

    def __init__(self, selection_boxes: Iterable[SelectionBox] = ()):
        self._selection_boxes = []

        if selection_boxes:
            for box in selection_boxes:
                self.add_box(box)

    def __iter__(self) -> Iterable[Tuple[int, int, int]]:
        return itertools.chain.from_iterable(sorted(self._selection_boxes, key=hash))

    def __len__(self):
        return len(self._selection_boxes)

    def __contains__(self, item: CoordinatesAny):
        for subbox in self._selection_boxes:
            if item in subbox:
                return True

        return False

    def __bool__(self):
        return bool(self._selection_boxes)

    @property
    def min(self) -> numpy.ndarray:
        if self._selection_boxes:
            return numpy.min(numpy.array([box.min for box in self._selection_boxes]), 0)
        else:
            raise ValueError("SelectionGroup does not contain any SubSelectionBoxes")

    @property
    def max(self) -> numpy.ndarray:
        if self._selection_boxes:
            return numpy.max(numpy.array([box.max for box in self._selection_boxes]), 0)
        else:
            raise ValueError("SelectionGroup does not contain any SubSelectionBoxes")

    def add_box(self, other: SelectionBox, do_merge_check: bool = True):
        """
        Adds a SelectionBox to the selection box. If `other` is next to another SelectionBox in the selection, matches in any 2 dimensions, and
        `do_merge_check` is True, then the 2 boxes will be combined into 1 box.

        :param other: The box to add
        :param do_merge_check: Boolean flag to merge boxes if able
        """
        # TODO: verify that this logic actually works on more complex cases
        if do_merge_check:
            boxes_to_remove = None
            new_box = None
            for box in self._selection_boxes:
                x_dim = box.min_x == other.min_x and box.max_x == other.max_x
                y_dim = box.min_y == other.min_y and box.max_y == other.max_y
                z_dim = box.min_z == other.min_z and box.max_z == other.max_z

                x_border = box.max_x == other.min_x or other.max_x == box.min_x
                y_border = box.max_y == other.min_y or other.max_y == box.min_y
                z_border = box.max_z == other.min_z or other.max_z == box.min_z

                if (
                    (x_dim and y_dim and z_border)
                    or (x_dim and z_dim and y_border)
                    or (y_dim and z_dim and x_border)
                ):
                    boxes_to_remove = box
                    new_box = SelectionBox(box.min, other.max)
                    break

            if new_box:
                self._selection_boxes.remove(boxes_to_remove)
                self.add_box(new_box)
            else:
                self._selection_boxes.append(other)
        else:
            self._selection_boxes.append(other)

    @property
    def is_contiguous(self) -> bool:
        """Does the SelectionGroup represent one connected region (True) or multiple separated regions (False)"""
        if len(self._selection_boxes) == 1:
            return True

        for i in range(len(self._selection_boxes) - 1):
            sub_box = self._selection_boxes[i]
            next_box = self._selection_boxes[i + 1]
            if (
                abs(sub_box.max_x - next_box.min_x)
                and abs(sub_box.max_y - next_box.min_y)
                and abs(sub_box.max_z - next_box.min_z)
            ):
                return False

        return True

    @property
    def is_rectangular(self) -> bool:
        """
        Checks if the SelectionGroup is a rectangle

        :return: True is the selection is a rectangle, False otherwise
        """
        return len(self._selection_boxes) == 1

    @property
    def selection_boxes(self) -> List[SelectionBox]:
        """
        Returns a list of unmodified SubSelectionBoxes in the SelectionGroup.
        :return: A list of the SubSelectionBoxes
        """
        return sorted(self._selection_boxes.copy(), key=hash)

    def chunk_locations(
        self, chunk_size: int = 16
    ) -> Generator[ChunkCoordinates, None, None]:
        """The chunk locations that the SelectionGroup is in.
        Each location is only given once even if there are multiple boxes in the chunk."""
        yield from set(
            location
            for box in self.selection_boxes
            for location in box.chunk_locations(chunk_size)
        )

    def _chunk_boxes(
        self, chunk_size: int = 16
    ) -> Dict[ChunkCoordinates, List[SelectionBox]]:
        boxes = {}
        for box in self.selection_boxes:
            for (cx, cz), sub_box in box.sub_sections(chunk_size):
                boxes.setdefault((cx, cz), []).append(sub_box)
        return boxes

    def sub_sections(
        self, chunk_size: int = 16
    ) -> Generator[Tuple[ChunkCoordinates, SelectionBox], None, None]:
        """A generator of modified `SelectionBox`es to fit within each sub-chunk.
        :param chunk_size: The dimension of the chunk (normally 16)
        """
        for (cx, cz), boxes in self._chunk_boxes(chunk_size).items():
            for box in boxes:
                yield (cx, cz), box

    def sub_slices(
        self, chunk_size: int = 16
    ) -> Generator[
        Tuple[ChunkCoordinates, Tuple[slice, slice, slice], SelectionBox], None, None
    ]:
        for (cx, cz), box in self.sub_sections(chunk_size):
            slices = box.chunk_slice(cx, cz, chunk_size)
            yield (cx, cz), slices, box

    def intersects(self, other: SelectionGroup) -> bool:
        """Check if self and other intersect"""
        return any(
            self_box.intersects(other_box)
            for self_box in self.selection_boxes
            for other_box in other.selection_boxes
        )

    def intersection(self, other: SelectionGroup) -> SelectionGroup:
        """Get a new SelectionGroup that represents the area contained within self and other"""
        intersection = SelectionGroup()
        for self_box in self.selection_boxes:
            for other_box in other.selection_boxes:
                if self_box.intersects(other_box):
                    intersection.add_box(self_box.intersection(other_box))
        return intersection

    def transform(self, scale: FloatTriplet, rotation: FloatTriplet) -> SelectionGroup:
        """creates a new transformed SelectionGroup."""
        selection_group = SelectionGroup()
        for selection in self.selection_boxes:
            for transformed_selection in selection.transform(scale, rotation):
                selection_group.add_box(transformed_selection)
        return selection_group


if __name__ == "__main__":
    b1 = SelectionBox((0, 0, 0), (4, 4, 4))
    b2 = SelectionBox((7, 7, 7), (10, 10, 10))
    sel_box = SelectionGroup((b1, b2))

    for x, y, z in sel_box:
        print(x, y, z)
