from __future__ import annotations

import itertools
import numpy

from typing import Tuple, Iterable, List, Generator, Union, Optional, overload

from amulet.api.data_types import (
    CoordinatesAny,
    ChunkCoordinates,
    SubChunkCoordinates,
    FloatTriplet,
    PointCoordinatesAny,
)
import amulet
from .box import SelectionBox


class SelectionGroup:
    """A container for zero or more `SelectionBox`es.
    This allows for non-rectangular and non-contiguous selections.
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

    def __repr__(self):
        boxes = ", ".join([repr(box) for box in self.selection_boxes])
        return f"SelectionGroup([{boxes}])"

    def __str__(self):
        boxes = ", ".join([str(box) for box in self.selection_boxes])
        return f"[{boxes}]"

    def __eq__(self, other: SelectionGroup) -> bool:
        return (
            type(other) is SelectionGroup
            and self.selection_boxes_sorted == other.selection_boxes_sorted
        )

    def __add__(self, other: SelectionGroup) -> SelectionGroup:
        if not type(other) is SelectionGroup:
            return NotImplemented
        return SelectionGroup(self.selection_boxes + other.selection_boxes)

    def __iter__(self) -> Iterable[SelectionBox]:
        """A generator of all the boxes in the group."""
        yield from self._selection_boxes

    def __len__(self) -> int:
        """The number of selection boxes in the group."""
        return len(self._selection_boxes)

    def __contains__(self, item: CoordinatesAny) -> bool:
        """Is the block (int) or point (float) location within any of the boxes in this group."""
        return self.contains_block(item)

    def contains_block(self, coords: CoordinatesAny) -> bool:
        """Is the coordinate greater than or equal to the min point but less than the max point of any of the boxes."""
        return any(box.contains_block(coords) for box in self._selection_boxes)

    def contains_point(self, coords: CoordinatesAny) -> bool:
        """Is the coordinate greater than or equal to the min point but less than or equal to the max point of any of the boxes."""
        return any(box.contains_point(coords) for box in self._selection_boxes)

    def blocks(self) -> Iterable[Tuple[int, int, int]]:
        """An iterable of every block in the selection.
        Note: if boxes intersect, the blocks in the intersected region will be included multiple times.
        If this behaviour is not desired the `merge_boxes` method will return a new SelectionGroup with no intersections."""
        return itertools.chain.from_iterable(self.selection_boxes)

    def __bool__(self) -> bool:
        """Are there any boxes in the group."""
        return bool(self._selection_boxes)

    @overload
    def __getitem__(self, item: int) -> SelectionBox:
        ...

    @overload
    def __getitem__(self, item: slice) -> SelectionGroup:
        ...

    def __getitem__(self, item):
        """Get the selection box at the given index."""
        val = self._selection_boxes[item]
        if type(val) is tuple:
            return SelectionGroup(val)
        else:
            return val

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

    def to_box(self) -> SelectionBox:
        """Create a `SelectionBox` based off the bounds of the boxes in the group."""
        return SelectionBox(self.min, self.max)

    def merge_boxes(self) -> SelectionGroup:
        """Take the boxes as they were given to this class, merge neighbouring boxes and remove overlapping regions.
        The result should be a SelectionGroup containing one or more SelectionBox classes that represents the same
        volume as the original but with no overlapping boxes."""
        selection_boxes = self.selection_boxes
        # TODO remove duplicate boxes

        # remove duplicates
        selection_boxes_ = []
        for box in selection_boxes:
            if not any(box == box_ for box_ in selection_boxes_):
                selection_boxes_.append(box)
        selection_boxes = selection_boxes_

        if len(selection_boxes) >= 2:
            merge_boxes = True
            while merge_boxes:
                # find two neighbouring boxes and merge them
                merge_boxes = False  # if two boxes get merged this will be set back to True and this will run again.
                box_index = 0  # the index of the first box
                while box_index < len(selection_boxes):
                    box = selection_boxes[box_index]
                    other_index = box_index + 1  # the index of the second box.
                    # This always starts at one greater than box_index because
                    # the lower values were already checked the other way around
                    while other_index < len(selection_boxes):
                        other = selection_boxes[other_index]
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
                            selection_boxes.pop(other_index)
                            selection_boxes.pop(box_index)
                            selection_boxes.append(
                                SelectionBox(
                                    numpy.min([box.min, other.min], 0),
                                    numpy.max([box.max, other.max], 0),
                                )
                            )
                            merge_boxes = True
                            box = selection_boxes[box_index]
                            other_index = box_index + 1
                        else:
                            other_index += 1
                    box_index += 1
        return SelectionGroup(selection_boxes)

    @property
    def is_contiguous(self) -> bool:
        """Does the SelectionGroup represent one connected region (True) or multiple separated regions (False).
        If two boxes are touching at the corners this is classed as contiguous."""
        # TODO: This needs some work. It will only work if the selections touch in a chain
        #  it does not care if it loops back and intersects itself. Does intersecting count as being contiguous?
        #  I would say yes
        if len(self._selection_boxes) == 1:
            return True

        for i in range(len(self._selection_boxes) - 1):
            sub_box: SelectionBox = self._selection_boxes[i]
            next_box: SelectionBox = self._selection_boxes[i + 1]
            if not sub_box.touches(next_box):
                return False

        return True

    @property
    def is_rectangular(self) -> bool:
        """
        Checks if the SelectionGroup is a rectangle

        :return: True is the selection is a rectangle, False otherwise
        """
        return (
            len(self._selection_boxes) == 1
            or len(self.merge_boxes().selection_boxes) == 1
        )

    @property
    def selection_boxes(self) -> List[SelectionBox]:
        """
        Returns a read only list of unmodified `SelectionBox`es in the SelectionGroup.
        :return: A list of the `SelectionBox`es
        """
        return list(self._selection_boxes)

    @property
    def selection_boxes_sorted(self) -> List[SelectionBox]:
        """
        Returns a list of unmodified `SelectionBox`es in the SelectionGroup sorted based on the hash of the coordinates.
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

    @staticmethod
    def _to_group(other: Union[SelectionGroup, SelectionBox]) -> SelectionGroup:
        if type(other) not in (SelectionGroup, SelectionBox):
            raise TypeError("other must be a SelectionGroup or SelectionBox.")
        if isinstance(other, SelectionBox):
            other = SelectionGroup(other)
        return other

    def intersection(
        self, other: Union[SelectionGroup, SelectionBox]
    ) -> SelectionGroup:
        """Get a new SelectionGroup that represents the area contained within self and other."""
        other = self._to_group(other)
        intersection = []
        for self_box in self.selection_boxes:
            for other_box in other.selection_boxes:
                if self_box.intersects(other_box):
                    intersection.append(self_box.intersection(other_box))
        return SelectionGroup(intersection)

    def subtract(self, other: Union[SelectionGroup, SelectionBox]) -> SelectionGroup:
        """Returns a new SelectionGroup containing the volume that does not intersect with other."""
        other = self._to_group(other)
        selections = self.selection_boxes
        for other_box in other.selection_boxes:
            # for each box in other
            selections_new = []
            for self_box in selections:
                selections_new += self_box.subtract(other_box)
            selections = selections_new
            if not selections:
                break
        return SelectionGroup(selections)

    def union(self, other: Union[SelectionGroup, SelectionBox]) -> SelectionGroup:
        """Returns a new SelectionGroup containing the volume of self and other."""
        other = self._to_group(other)
        if other.is_subset(self):
            return self
        else:
            return self.subtract(other) + other

    def is_subset(self, other: Union[SelectionGroup, SelectionBox]) -> bool:
        """Is self completely within other."""
        other = self._to_group(other)
        return not self.subtract(other)

    def closest_vector_intersection(
        self, origin: PointCoordinatesAny, vector: PointCoordinatesAny
    ) -> Tuple[Optional[int], float]:
        """
        Returns the index for the closest box in the look vector and the multiplier of the look vector to get there.
        :param origin: The origin tuple of the vector
        :param vector: The vector magnitude in x, y and z
        :return: Index for the closest box and the multiplier of the vector to get there. None, inf if no intersection.
        """
        index_return = None
        multiplier = float("inf")
        for index, box in enumerate(self._selection_boxes):
            mult = box.intersects_vector(origin, vector)
            if mult is not None and mult < multiplier:
                multiplier = mult
                index_return = index
        return index_return, multiplier

    def transform(
        self, scale: FloatTriplet, rotation: FloatTriplet, translation: FloatTriplet
    ) -> SelectionGroup:
        """creates a new transformed SelectionGroup."""
        selection_group = []
        for selection in self.selection_boxes:
            for transformed_selection in selection.transform(
                scale, rotation, translation
            ):
                selection_group.append(transformed_selection)
        return SelectionGroup(selection_group)

    def copy(self):
        return SelectionGroup(self.selection_boxes)

    @property
    def volume(self) -> int:
        """The volume of all the selection boxes combined."""
        return sum(box.volume for box in self.selection_boxes)

    @property
    def footprint_area(self) -> int:
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
