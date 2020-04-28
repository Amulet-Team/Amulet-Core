from __future__ import annotations

import itertools
import numpy

from typing import Sequence, Tuple, Union, Iterable, List, Generator

from .minecraft_types import Point
from ..utils.world_utils import (
    block_coords_to_chunk_coords,
    blocks_slice_to_chunk_slice,
)


class SubSelectionBox:
    """
    A SubSelectionBox is a box that can represent the entirety of a Selection or just a subsection
    of one. This allows for non-rectangular and non-contiguous selections.

    The both the minimum and  maximum coordinate points are inclusive.
    """

    def __init__(self, min_point: Point, max_point: Point):
        box = numpy.array([min_point, max_point], dtype=numpy.int)
        self._min_x, self._min_y, self._min_z = numpy.min(box, 0).tolist()
        self._max_x, self._max_y, self._max_z = numpy.max(box, 0).tolist()

    @classmethod
    def chunk_box(
        cls, cx: int, cz: int, chunk_size: int
    ):
        """Get a SubSelectionBox containing the whole of a given chunk"""
        return cls(
            (cx * chunk_size, -(2**30), cz * chunk_size),
            ((cx + 1) * chunk_size, 2**30, (cz + 1) * chunk_size),
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

    def __contains__(
        self, item: Union[Point, Tuple[int, int, int], Tuple[float, float, float]]
    ):
        return (
            self._min_x <= item[0] < self._max_x
            and self._min_y <= item[1] < self._max_y
            and self._min_z <= item[2] < self._max_z
        )

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
            self,
            cx: int,
            cz: int,
            chunk_size: int = 16
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
    def size_x(self) -> int:
        """The length of the box in the x axis"""
        return self._max_x - self._min_x

    @property
    def size_y(self) -> int:
        """The length of the box in the y axis"""
        return self._max_y - self._min_z

    @property
    def size_z(self) -> int:
        """The length of the box in the z axis"""
        return self._max_z - self._min_z

    @property
    def shape(self) -> Tuple[int, int, int]:
        """The shape of the box"""
        return self.size_x, self.size_y, self.size_z

    def intersects(self, other: SubSelectionBox) -> bool:
        """
        Method to check whether this instance of SubSelectionBox intersects another SubSelectionBox

        :param other: The other SubSelectionBox to check for intersection
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

    def intersection(self, other: SubSelectionBox) -> SubSelectionBox:
        """Get a SubSelectionBox that represents the region contained within self and other.
        Box may be a zero width box. Use self.intersects to check that it actually intersects."""
        return SubSelectionBox(
            numpy.min([numpy.max([self.min, other.max], 0), self.max], 0),
            numpy.max([numpy.min([self.max, other.min], 0), self.min], 0),
        )


class Selection:
    """
    Holding class for multiple SubSelectionBoxes which allows for non-rectangular and non-contiguous selections
    """

    def __init__(self, boxes: Sequence[SubSelectionBox] = None):
        self._boxes = []

        if boxes:
            for box in boxes:
                self.add_box(box)

    def __iter__(self) -> Iterable[Tuple[int, int, int]]:
        return itertools.chain.from_iterable(sorted(self._boxes, key=hash))

    def __len__(self):
        return len(self._boxes)

    def __contains__(self, item: Union[Point, Tuple[int, int, int]]):
        for subbox in self._boxes:
            if item in subbox:
                return True

        return False

    @property
    def min(self) -> numpy.ndarray:
        if self._boxes:
            return numpy.min(numpy.array([box.min for box in self._boxes]), 0)
        else:
            raise ValueError("Selection does not contain any SubSelectionBoxes")

    @property
    def max(self) -> numpy.ndarray:
        if self._boxes:
            return numpy.max(numpy.array([box.max for box in self._boxes]), 0)
        else:
            raise ValueError("Selection does not contain any SubSelectionBoxes")

    def add_box(self, other: SubSelectionBox, do_merge_check: bool = True):
        """
        Adds a SubSelectionBox to the selection box. If `other` is next to another SubSelectionBox in the selection, matches in any 2 dimensions, and
        `do_merge_check` is True, then the 2 boxes will be combined into 1 box.

        :param other: The box to add
        :param do_merge_check: Boolean flag to merge boxes if able
        """
        # TODO: verify that this logic actually works on more complex cases
        if do_merge_check:
            boxes_to_remove = None
            new_box = None
            for box in self._boxes:
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
                    new_box = SubSelectionBox(box.min, other.max)
                    break

            if new_box:
                self._boxes.remove(boxes_to_remove)
                self.add_box(new_box)
            else:
                self._boxes.append(other)
        else:
            self._boxes.append(other)

    @property
    def is_contiguous(self) -> bool:
        """Does the Selection represent one connected region (True) or multiple separated regions (False)"""
        if len(self._boxes) == 1:
            return True

        for i in range(len(self._boxes) - 1):
            sub_box = self._boxes[i]
            next_box = self._boxes[i + 1]
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
        Checks if the Selection is a rectangle

        :return: True is the selection is a rectangle, False otherwise
        """
        return len(self._boxes) == 1

    @property
    def subboxes(self) -> List[SubSelectionBox]:
        """
        Returns a list of unmodified SubSelectionBoxes in the Selection.
        :return: A list of the SubSelectionBoxes
        """
        return sorted(self._boxes, key=hash)

    def sub_sections(self, chunk_size=16) -> Generator[Tuple[Tuple[int, int], SubSelectionBox], None, None]:
        """A generator of modified `SubSelectionBox`es to fit within each sub-chunk.
        :param chunk_size: The dimension of the chunk (normally 16)
        """
        for box in self.subboxes:  # TODO: optimise this so that it yields all boxes for a chunk in one go
            first_chunk = block_coords_to_chunk_coords(box.min_x, box.min_z)
            last_chunk = block_coords_to_chunk_coords(box.max_x - 1, box.max_z - 1)
            for cx, cz in itertools.product(
                range(first_chunk[0], last_chunk[0] + 1),
                range(first_chunk[1], last_chunk[1] + 1),
            ):
                yield (cx, cz), box.intersection(SubSelectionBox.chunk_box(cx, cz, chunk_size))  # TODO: modify this so that it yields one box per sub-chunk

    def sub_slices(self, chunk_size=16) -> Generator[Tuple[Tuple[int, int], Tuple[slice, slice, slice], SubSelectionBox], None, None]:
        for (cx, cz), box in self.sub_sections(chunk_size):
            slices = box.chunk_slice(cx, cz, chunk_size)
            yield (cx, cz), slices, box

    def intersects(self, other: Selection) -> bool:
        """Check if self and other intersect"""
        return any(
            self_box.intersects(other_box)
            for self_box in self.subboxes
            for other_box in other.subboxes
        )

    def intersection(self, other: Selection) -> Selection:
        """Get a new Selection that represents the area contained within self and other"""
        intersection = Selection()
        for self_box in self.subboxes:
            for other_box in other.subboxes:
                if self_box.intersects(other_box):
                    intersection.add_box(self_box.intersection(other_box))
        return intersection


if __name__ == "__main__":
    b1 = SubSelectionBox((0, 0, 0), (4, 4, 4))
    b2 = SubSelectionBox((7, 7, 7), (10, 10, 10))
    sel_box = Selection((b1, b2))

    for x, y, z in sel_box:
        print(x, y, z)
