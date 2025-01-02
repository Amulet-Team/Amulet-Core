from __future__ import annotations

import numpy

from typing import Iterable, Iterator, overload, Any
import warnings

from amulet.data_types import (
    BlockCoordinates,
    ChunkCoordinates,
    SubChunkCoordinates,
    FloatTriplet,
)
from amulet.data_types import (
    PointCoordinates,
    PointCoordinatesArray,
)
from .abstract_selection import AbstractBaseSelection
from .box import SelectionBox


class SelectionGroup(AbstractBaseSelection, Iterable[SelectionBox]):
    """
    A container for zero or more :class:`SelectionBox` instances.

    This allows for non-rectangular and non-contiguous selections.
    """

    _selection_boxes: tuple[SelectionBox, ...]

    def __add__(self, boxes: Iterable[SelectionBox]) -> SelectionGroup:
        """
        Add an iterable of :class:`SelectionBox` classes to this :class:`SelectionGroup`.

        Note this will construct a new :class:`SelectionGroup` because it is immutable so cannot be modified in place.

        >>> group1 = SelectionGroup(SelectionBox((-1, -1, -1), (0, 0, 0)))
        >>> group2 = SelectionGroup([
        >>>     SelectionBox((0, 0, 0), (1, 1, 1)),
        >>>     SelectionBox((1, 1, 1), (2, 2, 2))
        >>> ])
        >>> group1 + group2
        SelectionGroup([SelectionBox((-1, -1, -1), (0, 0, 0)), SelectionBox((0, 0, 0), (1, 1, 1)), SelectionBox((1, 1, 1), (2, 2, 2))])
        >>> group1 += group2
        >>> group1
        SelectionGroup([SelectionBox((-1, -1, -1), (0, 0, 0)), SelectionBox((0, 0, 0), (1, 1, 1)), SelectionBox((1, 1, 1), (2, 2, 2))])

        :param boxes: An iterable of boxes to add to this group.
        :return: A new :class:`SelectionGroup` class containing the boxes from this instance and those in ``boxes``.
        """
        try:
            boxes = tuple(boxes)
        except:
            return NotImplemented
        if not all(isinstance(b, SelectionBox) for b in boxes):
            return NotImplemented
        return SelectionGroup(tuple(self) + boxes)

    @property
    def blocks(self) -> Iterator[BlockCoordinates]:
        """
        The location of every block in the selection.

        >>> group: SelectionGroup
        >>> for x, y, z in group.blocks:
        >>>     ...

        Note: if boxes intersect, the blocks in the intersected region will be included multiple times.

        If this behaviour is not desired the :meth:`merge_boxes` method will return a new SelectionGroup with no intersections.

        >>> for x, y, z in group.merge_boxes().blocks:
        >>>     ...

        :return: An iterable of block locations.
        """
        for box in self.selection_boxes:
            for coord in box.blocks:
                yield coord

    def merge_boxes(self) -> SelectionGroup:
        """
        Take the boxes as they were given to this class, merge neighbouring boxes and remove overlapping regions.

        The result should be a SelectionGroup containing one or more SelectionBox classes that represents the same
        volume as the original but with no overlapping boxes.
        """
        # remove duplicates
        selection_boxes: list[SelectionBox] = []
        for box in self.selection_boxes:
            if not any(box == box_ for box_ in selection_boxes):
                selection_boxes.append(box)

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

    def chunk_count(self, sub_chunk_size: int = 16) -> int:
        return len(self.chunk_locations(sub_chunk_size))

    def chunk_locations(self, sub_chunk_size: int = 16) -> set[ChunkCoordinates]:
        return set(
            location
            for box in self.selection_boxes
            for location in box.chunk_locations(sub_chunk_size)
        )

    def chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterator[tuple[ChunkCoordinates, SelectionBox]]:
        for box in self.selection_boxes:
            yield from box.chunk_boxes(sub_chunk_size)

    def sub_chunk_count(self, sub_chunk_size: int = 16) -> int:
        return len(self.sub_chunk_locations(sub_chunk_size))

    def sub_chunk_locations(self, sub_chunk_size: int = 16) -> set[SubChunkCoordinates]:
        return set(
            location
            for box in self.selection_boxes
            for location in box.sub_chunk_locations(sub_chunk_size)
        )

    def sub_chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterator[tuple[SubChunkCoordinates, SelectionBox]]:
        for box in self.selection_boxes:
            for (cx, cy, cz), sub_box in box.sub_chunk_boxes(sub_chunk_size):
                yield (cx, cy, cz), box

    def intersection(self, other: AbstractBaseSelection) -> SelectionGroup:
        return self._intersection(other)

    def _intersection(self, other: AbstractBaseSelection) -> SelectionGroup:
        group = other.selection_group()
        intersection: list[SelectionBox] = []
        for self_box in self.selection_boxes:
            for other_box in group:
                if self_box.intersects(other_box):
                    intersection.append(self_box.intersection(other_box))
        return SelectionGroup(intersection)

    def subtract(self, other: AbstractBaseSelection) -> SelectionGroup:
        """
        Returns a new :class:`SelectionGroup` containing the volume that does not intersect with other.

        This may be empty if other fully contains self or equal to self if they do not intersect.

        :param other: The :class:`SelectionBox` or :class:`SelectionGroup` to subtract.
        """
        return self._subtract(other)

    def _subtract(self, other: AbstractBaseSelection) -> SelectionGroup:
        group = other.selection_group()
        selections = self
        for other_box in group:
            # for each box in other
            selections_new = SelectionGroup()
            for self_box in selections:
                selections_new += self_box.subtract(other_box)
            selections = selections_new
            if not selections:
                break
        return selections

    def union(self, other: AbstractBaseSelection) -> SelectionGroup:
        """
        Returns a new SelectionGroup containing the volume of self and other.

        :param other: The other selection to add to this one.
        """
        group = other.selection_group()
        if group.is_subset(self):
            return self
        else:
            return self.subtract(group) + group

    def is_subset(self, other: AbstractBaseSelection) -> bool:
        """
        Is this selection completely contained within ``other``.

        :param other: The other selection to test against.
        :return: True if this selection completely fits in other.
        """
        return not self.subtract(other.selection_group())

    def closest_vector_intersection(
        self,
        origin: PointCoordinates | PointCoordinatesArray,
        direction: PointCoordinates | PointCoordinatesArray,
    ) -> tuple[int | None, float]:
        """
        Returns the index for the closest box in the look vector and the multiplier of the look vector to get there.

        :param origin: The origin of the vector
        :param direction: The vector magnitude in x, y and z
        :return: Index for the closest box and the multiplier of the vector to get there. None, inf if no intersection.
        """
        index_return = None
        multiplier = float("inf")
        for index, box in enumerate(self._selection_boxes):
            mult = box.intersects_vector(origin, direction)
            if mult is not None and mult < multiplier:
                multiplier = mult
                index_return = index
        return index_return, multiplier

    def transform(
        self, scale: FloatTriplet, rotation: FloatTriplet, translation: FloatTriplet
    ) -> SelectionGroup:
        """
        Creates a new :class:`SelectionGroup` transformed by the given inputs.

        :param scale: A tuple of scaling factors in the x, y and z axis.
        :param rotation: The rotation about the x, y and z axis in radians.
        :param translation: The translation about the x, y and z axis.
        :return: A new :class:`~amulet.api.selection.SelectionGroup` representing the transformed selection.
        """
        selection_group = SelectionGroup()
        for selection in self.selection_boxes:
            selection_group += selection.transform(scale, rotation, translation)
        return selection_group

    @property
    def volume(self) -> int:
        return sum(box.volume for box in self.selection_boxes)

    @property
    def footprint_area(self) -> int:
        """
        The 2D area that the selection fills when looking at the selection from above.
        """
        return (
            SelectionGroup(
                [
                    SelectionBox((box.min_x, 0, box.min_z), (box.max_x, 1, box.max_z))
                    for box in self.selection_boxes
                ]
            )
            .merge_boxes()
            .volume
        )
