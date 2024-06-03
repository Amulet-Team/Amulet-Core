from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Iterator, TYPE_CHECKING, Any
import numpy

from amulet.data_types import (
    ChunkCoordinates,
    SubChunkCoordinates,
    FloatTriplet,
    BlockCoordinates,
)

if TYPE_CHECKING:
    from .box import SelectionBox
    from .group import SelectionGroup


class AbstractBaseSelection(ABC):
    """
    A parent selection class to force a consistent API for selection group and box.
    """

    __slots__ = ()

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """
        Is the selection equal to the other selection.

        >>> selection1: AbstractBaseSelection
        >>> selection2: AbstractBaseSelection
        >>> selection1 == selection2
        True

        :param other: The other selection to test.
        :return: True if the selections are the same, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def blocks(self) -> Iterator[BlockCoordinates]:
        """
        The location of every block in the selection.

        :return: An Iterator of block locations.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def bounds(self) -> tuple[BlockCoordinates, BlockCoordinates]:
        """
        The minimum and maximum points in the selection.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def bounds_array(self) -> numpy.ndarray:
        """
        The minimum and maximum points in the selection as a numpy array.
        """
        raise NotImplementedError

    @abstractmethod
    def bounding_box(self) -> SelectionBox:
        """Get a SelectionBox that contains this selection."""
        raise NotImplementedError

    @abstractmethod
    def selection_group(self) -> SelectionGroup:
        """Get this selection as a SelectionGroup."""
        raise NotImplementedError

    @abstractmethod
    def chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterator[tuple[ChunkCoordinates, SelectionBox]]:
        """
        An Iterator of chunk coordinates and boxes that intersect the selection and the chunk.

        >>> selection1: AbstractBaseSelection
        >>> for (cx, cz), box in selection1.chunk_boxes():
        >>>     ...

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
        raise NotImplementedError

    @abstractmethod
    def chunk_count(self, sub_chunk_size: int = 16) -> int:
        """
        The number of chunks that intersect the selection.

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
        raise NotImplementedError

    @abstractmethod
    def chunk_locations(self, sub_chunk_size: int = 16) -> Iterable[ChunkCoordinates]:
        """
        An iterable of chunk coordinates that intersect the selection.

        >>> selection1: AbstractBaseSelection
        >>> for cx, cz in selection1.chunk_locations():
        >>>     ...

        :param sub_chunk_size:  The dimension of a sub-chunk. Default 16.
        """
        raise NotImplementedError

    @abstractmethod
    def contains_block(self, x: int, y: int, z: int) -> bool:
        """
        Is the block contained within the selection.

        >>> selection1: AbstractBaseSelection
        >>> (1, 2, 3) in selection1
        True

        :param x: The x coordinate of the block. Defined by the most negative corner.
        :param y: The y coordinate of the block. Defined by the most negative corner.
        :param z: The z coordinate of the block. Defined by the most negative corner.
        :return: True if the block is in the selection.
        """
        raise NotImplementedError

    @abstractmethod
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """
        Is the point contained within the selection.

        >>> selection1: AbstractBaseSelection
        >>> (1.5, 2.5, 3.5) in selection1
        True

        :param x: The x coordinate of the point.
        :param y: The y coordinate of the point.
        :param z: The z coordinate of the point.
        :return: True if the point is in the selection.
        """
        raise NotImplementedError

    def intersection(self, other: AbstractBaseSelection) -> AbstractBaseSelection:
        """
        Create and return a new a selection containing the volume that this selection and other both contain.

        If the selections do not intersect the returned selection will have no volume.

        Use :meth:`intersects` to test if the two selections intersect.

        :param other: The other selection.
        :return: A new selection containing the intersection.
        """
        out = self._intersection(other)
        if out is NotImplemented:
            out = other._intersection(self)
        if out is NotImplemented:
            raise TypeError(
                f"intersection is not supported between instances of type {self.__class__} and {other.__class__}"
            )
        return out

    @abstractmethod
    def _intersection(self, other: AbstractBaseSelection) -> AbstractBaseSelection:
        """Get the intersection between self and other.

        :param other: The other selection
        :return: The selection that intersects. NotImplemented if the operation is not supported.
        """

    def intersects(self, other: AbstractBaseSelection) -> bool:
        """
        Does this selection intersect ``other``.

        :param other: The other selection.
        :return: True if the selections intersect, False otherwise.
        """
        out = self._intersects(other)
        if out is NotImplemented:
            out = other._intersects(self)
        if out is NotImplemented:
            raise TypeError(
                f"intersects is not supported between instances of type {self.__class__} and {other.__class__}"
            )
        return out

    @abstractmethod
    def _intersects(self, other: AbstractBaseSelection) -> bool:
        """Check if other intersects this instance.

        :param other: The other selection to test
        :return: True if intersects, False if not intersects and NotImplemented if the operation is not supported.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def max(self) -> BlockCoordinates:
        """
        The maximum point in the selection.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def max_array(self) -> numpy.ndarray:
        """
        The maximum point in the selection as a numpy array.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def max_x(self) -> int:
        """
        The maximum x coordinate of the selection.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def max_y(self) -> int:
        """
        The maximum y coordinate of the selection.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def max_z(self) -> int:
        """
        The maximum z coordinate of the selection.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def min(self) -> BlockCoordinates:
        """
        The minimum point in the selection.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def min_array(self) -> numpy.ndarray:
        """
        The minimum point in the selection as a numpy array.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def min_x(self) -> int:
        """
        The minimum x coordinate of the selection.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def min_y(self) -> int:
        """
        The minimum y coordinate of the selection.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def min_z(self) -> int:
        """
        The minimum z coordinate of the selection.
        """
        raise NotImplementedError

    @abstractmethod
    def sub_chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterator[tuple[SubChunkCoordinates, SelectionBox]]:
        """
        An Iterator of sub-chunk coordinates and boxes that intersect the selection and the sub-chunk.

        >>> selection1: AbstractBaseSelection
        >>> for (cx, cy, cz), box in selection1.sub_chunk_boxes():
        >>>     ...

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
        raise NotImplementedError

    @abstractmethod
    def sub_chunk_count(self, sub_chunk_size: int = 16) -> int:
        """
        The number of sub-chunks that intersect the selection.

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
        raise NotImplementedError

    @abstractmethod
    def sub_chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Iterable[SubChunkCoordinates]:
        """
        An iterable of sub-chunk coordinates that intersect the selection.

        >>> selection1: AbstractBaseSelection
        >>> for cx, cy, cz in selection1.sub_chunk_locations():
        >>>     ...

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
        raise NotImplementedError

    @abstractmethod
    def subtract(self, other: AbstractBaseSelection) -> AbstractBaseSelection:
        raise NotImplementedError

    @abstractmethod
    def transform(
        self, scale: FloatTriplet, rotation: FloatTriplet, translation: FloatTriplet
    ) -> AbstractBaseSelection:
        raise NotImplementedError

    @property
    @abstractmethod
    def volume(self) -> int:
        """
        The number of blocks in the selection.
        """
        raise NotImplementedError
