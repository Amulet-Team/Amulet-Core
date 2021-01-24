from __future__ import annotations

import itertools
import numpy

from typing import Tuple, Iterable, List, Generator, Union

from amulet.api.data_types import (
    CoordinatesAny,
    ChunkCoordinates,
    SubChunkCoordinates,
    FloatTriplet,
)
import amulet
from .box import SelectionBox


class SelectionGroup:
    """
    Holding class for multiple `SelectionBox`es which allows for non-rectangular and non-contiguous selections
    """

    def __init__(
        self, selection_boxes: Union[SelectionBox, Iterable[SelectionBox]] = ()
    ):
        if type(selection_boxes) is SelectionBox:
            self._selection_boxes: Tuple[SelectionBox, ...] = (selection_boxes,)
        elif type(selection_boxes) in (tuple, list):
            self._selection_boxes: Tuple[SelectionBox, ...] = tuple(
                box for box in selection_boxes if type(box) is SelectionBox
            )
        else:
            amulet.log.warning(f"Invalid format for selection_boxes {selection_boxes}")
            self._selection_boxes: Tuple[SelectionBox, ...] = ()

    def __iter__(self) -> Iterable[Tuple[int, int, int]]:
        """A generator of all the block locations in every box in the group."""
        return itertools.chain.from_iterable(self.selection_boxes)

    def __len__(self):
        """The number of selection boxes in the group."""
        return len(self._selection_boxes)

    def __contains__(self, item: CoordinatesAny):
        """Is the block (int) or point (float) location within any of the boxes in this group."""
        return any(item in box for box in self._selection_boxes)

    def __bool__(self):
        """Are there any boxes in the group."""
        return bool(self._selection_boxes)

    @property
    def min(self) -> numpy.ndarray:
        """The minimum point of of all the boxes in the group."""
        if self._selection_boxes:
            return numpy.min(numpy.array([box.min for box in self._selection_boxes]), 0)
        else:
            raise ValueError("SelectionGroup does not contain any SelectionBoxes")

    @property
    def max(self) -> numpy.ndarray:
        """The maximum point of of all the boxes in the group."""
        if self._selection_boxes:
            return numpy.max(numpy.array([box.max for box in self._selection_boxes]), 0)
        else:
            raise ValueError("SelectionGroup does not contain any SelectionBoxes")


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
        Returns a list of unmodified `SelectionBox`es in the SelectionGroup.
        :return: A list of the `SelectionBox`es
        """
        return sorted(self._selection_boxes, key=hash)

    def chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Generator[ChunkCoordinates, None, None]:
        """A generator of chunk locations that the boxes in this group intersect.
        Each location is only given once even if there are multiple boxes in the chunk.
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        yield from set(
            location
            for box in self.selection_boxes
            for location in box.chunk_locations(sub_chunk_size)
        )

    def chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Generator[Tuple[ChunkCoordinates, SelectionBox], None, None]:
        """A generator of modified `SelectionBox`es to fit within each chunk.
        If a box straddles multiple chunks this method will split it up into a box
        for each chunk it intersects along with the chunk coordinates of that chunk.
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        for box in self.selection_boxes:
            yield from box.chunk_boxes(sub_chunk_size)

    def sub_chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Generator[SubChunkCoordinates, None, None]:
        """A generator of sub-chunk locations that the boxes in this group intersect.
        Each location is only given once even if there are multiple boxes in the chunk.
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        yield from set(
            location
            for box in self.selection_boxes
            for location in box.sub_chunk_locations(sub_chunk_size)
        )

    def sub_chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Generator[Tuple[SubChunkCoordinates, SelectionBox], None, None]:
        """A generator of modified `SelectionBox`es to fit within each sub-chunk.
        If a box straddles multiple sub-chunks this method will split it up into a box
        for each sub-chunk it intersects along with the sub-chunk coordinates of that sub-chunk.
        :param sub_chunk_size: The dimension of the chunk (normally 16)
        """
        for box in self.selection_boxes:
            for (cx, cy, cz), sub_box in box.sub_chunk_boxes(sub_chunk_size):
                yield (cx, cy, cz), box

    def intersects(self, other: Union[SelectionGroup, SelectionBox]) -> bool:
        """Check if self and other intersect."""
        if isinstance(other, SelectionGroup):
            return any(
                self_box.intersects(other_box)
                for self_box in self.selection_boxes
                for other_box in other.selection_boxes
            )
        elif isinstance(other, SelectionBox):
            return any(self_box.intersects(other) for self_box in self.selection_boxes)

    def intersection(
        self, other: Union[SelectionGroup, SelectionBox]
    ) -> SelectionGroup:
        """Get a new SelectionGroup that represents the area contained within self and other."""
        intersection = SelectionGroup()
        if isinstance(other, SelectionGroup):
            for self_box in self.selection_boxes:
                for other_box in other.selection_boxes:
                    if self_box.intersects(other_box):
                        intersection.add_box(self_box.intersection(other_box))
        elif isinstance(other, SelectionBox):
            for self_box in self.selection_boxes:
                if self_box.intersects(other):
                    intersection.add_box(self_box.intersection(other))
        return intersection

    def transform(
        self, scale: FloatTriplet, rotation: FloatTriplet, translation: FloatTriplet
    ) -> SelectionGroup:
        """creates a new transformed SelectionGroup."""
        selection_group = SelectionGroup()
        for selection in self.selection_boxes:
            for transformed_selection in selection.transform(
                scale, rotation, translation
            ):
                selection_group.add_box(transformed_selection)
        return selection_group

    def copy(self):
        return SelectionGroup([box for box in self.selection_boxes])

    @property
    def volume(self) -> int:
        """The volume of all the selection boxes combined."""
        return sum(box.volume for box in self.selection_boxes)

    @property
    def footprint_area(self):
        """The flat area of the selection."""
        return SelectionGroup(
            [
                SelectionBox((box.min_x, 0, box.min_z), (box.max_x, 1, box.max_z))
                for box in self.selection_boxes
            ]
        ).volume


if __name__ == "__main__":
    b1 = SelectionBox((0, 0, 0), (4, 4, 4))
    b2 = SelectionBox((7, 7, 7), (10, 10, 10))
    sel_box = SelectionGroup((b1, b2))

    for x, y, z in sel_box:
        print(x, y, z)
