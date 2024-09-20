from typing import Any, Iterable, Iterator, overload

import numpy
from amulet.data_types import BlockCoordinates as BlockCoordinates
from amulet.data_types import ChunkCoordinates as ChunkCoordinates
from amulet.data_types import FloatTriplet as FloatTriplet
from amulet.data_types import PointCoordinates as PointCoordinates
from amulet.data_types import PointCoordinatesArray as PointCoordinatesArray
from amulet.data_types import SubChunkCoordinates as SubChunkCoordinates

from .abstract_selection import AbstractBaseSelection as AbstractBaseSelection
from .box import SelectionBox as SelectionBox

class SelectionGroup(AbstractBaseSelection, Iterable[SelectionBox]):
    """
    A container for zero or more :class:`SelectionBox` instances.

    This allows for non-rectangular and non-contiguous selections.
    """

    def __init__(
        self, selection_boxes: SelectionBox | Iterable[SelectionBox] = ()
    ) -> None:
        """
        Construct a new :class:`SelectionGroup` class from the given data.

        >>> SelectionGroup(SelectionBox((0, 0, 0), (1, 1, 1)))
        >>> SelectionGroup([
        >>>     SelectionBox((0, 0, 0), (1, 1, 1)),
        >>>     SelectionBox((1, 1, 1), (2, 2, 2))
        >>> ])

        :param selection_boxes: A :class:`SelectionBox` or iterable of :class:`SelectionBox` classes.
        """

    def __eq__(self, other: Any) -> bool:
        """
        Does the contents of this :class:`SelectionGroup` match the other :class:`SelectionGroup`.

        Note if the boxes do not exactly match this will return False even if the volume represented is the same.

        :param other: The other :class:`SelectionGroup` to compare with.
        :return: True if the boxes contained match.
        """

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

    def __iter__(self) -> Iterator[SelectionBox]:
        """An iterable of all the :class:`SelectionBox` classes in the group."""

    def __len__(self) -> int:
        """The number of :class:`SelectionBox` classes in the group."""

    def contains_block(self, x: int, y: int, z: int) -> bool: ...
    def contains_point(self, x: float, y: float, z: float) -> bool: ...
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

    def __bool__(self) -> bool:
        """Are there any boxes in the group."""

    @overload
    def __getitem__(self, item: int) -> SelectionBox: ...
    @overload
    def __getitem__(self, item: slice) -> SelectionGroup: ...
    @property
    def min(self) -> BlockCoordinates:
        """The minimum point of all the boxes in the group."""

    @property
    def min_array(self) -> numpy.ndarray:
        """The minimum point of all the boxes in the group as a numpy array."""

    @property
    def min_x(self) -> int: ...
    @property
    def min_y(self) -> int: ...
    @property
    def min_z(self) -> int: ...
    @property
    def max(self) -> BlockCoordinates:
        """The maximum point of all the boxes in the group."""

    @property
    def max_array(self) -> numpy.ndarray:
        """The maximum point of all the boxes in the group as a numpy array."""

    @property
    def max_x(self) -> int: ...
    @property
    def max_y(self) -> int: ...
    @property
    def max_z(self) -> int: ...
    @property
    def bounds(self) -> tuple[BlockCoordinates, BlockCoordinates]: ...
    @property
    def bounds_array(self) -> numpy.ndarray: ...
    def to_box(self) -> SelectionBox:
        """Create a `SelectionBox` based off the bounds of the boxes in the group."""

    def bounding_box(self) -> SelectionBox: ...
    def selection_group(self) -> SelectionGroup: ...
    def merge_boxes(self) -> SelectionGroup:
        """
        Take the boxes as they were given to this class, merge neighbouring boxes and remove overlapping regions.

        The result should be a SelectionGroup containing one or more SelectionBox classes that represents the same
        volume as the original but with no overlapping boxes.
        """

    @property
    def is_contiguous(self) -> bool:
        """
        Does the SelectionGroup represent one connected region (True) or multiple separated regions (False).

        If two boxes are touching at the corners this is classed as contiguous.
        """

    @property
    def is_rectangular(self) -> bool:
        """
        Checks if the SelectionGroup is a rectangle

        :return: True is the selection is a rectangle, False otherwise
        """

    @property
    def selection_boxes(self) -> tuple[SelectionBox, ...]:
        """
        A tuple of the :class:`SelectionBox` instances stored for this group.
        """

    @property
    def selection_boxes_sorted(self) -> list[SelectionBox]:
        """
        A list of the :class:`SelectionBox` instances for this group sorted by their hash.
        """

    def chunk_count(self, sub_chunk_size: int = 16) -> int: ...
    def chunk_locations(self, sub_chunk_size: int = 16) -> set[ChunkCoordinates]: ...
    def chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterator[tuple[ChunkCoordinates, SelectionBox]]: ...
    def sub_chunk_count(self, sub_chunk_size: int = 16) -> int: ...
    def sub_chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> set[SubChunkCoordinates]: ...
    def sub_chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterator[tuple[SubChunkCoordinates, SelectionBox]]: ...
    def intersection(self, other: AbstractBaseSelection) -> SelectionGroup: ...
    def subtract(self, other: AbstractBaseSelection) -> SelectionGroup:
        """
        Returns a new :class:`SelectionGroup` containing the volume that does not intersect with other.

        This may be empty if other fully contains self or equal to self if they do not intersect.

        :param other: The :class:`SelectionBox` or :class:`SelectionGroup` to subtract.
        """

    def union(self, other: AbstractBaseSelection) -> SelectionGroup:
        """
        Returns a new SelectionGroup containing the volume of self and other.

        :param other: The other selection to add to this one.
        """

    def is_subset(self, other: AbstractBaseSelection) -> bool:
        """
        Is this selection completely contained within ``other``.

        :param other: The other selection to test against.
        :return: True if this selection completely fits in other.
        """

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

    @property
    def volume(self) -> int: ...
    @property
    def footprint_area(self) -> int:
        """
        The 2D area that the selection fills when looking at the selection from above.
        """
