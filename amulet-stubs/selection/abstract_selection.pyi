import abc
import numpy
from .box import SelectionBox as SelectionBox
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amulet.api.data_types import BlockCoordinates as BlockCoordinates, ChunkCoordinates as ChunkCoordinates, CoordinatesAny as CoordinatesAny, FloatTriplet as FloatTriplet, SubChunkCoordinates as SubChunkCoordinates
from typing import Iterable, Tuple

class AbstractBaseSelection(ABC, metaclass=abc.ABCMeta):
    """
    A parent selection class to force a consistent API for selection group and box.
    """
    __slots__: Incomplete
    @abstractmethod
    def __eq__(self, other) -> bool:
        """
        Is the selection equal to the other selection.

        >>> selection1 == selection2
        True

        :param other: The other selection to test.
        :return: True if the selections are the same, False otherwise.
        """
    @abstractmethod
    def __repr__(self) -> str: ...
    @abstractmethod
    def __str__(self) -> str: ...
    @property
    @abstractmethod
    def blocks(self) -> Iterable[BlockCoordinates]:
        """
        The location of every block in the selection.

        :return: An iterable of block locations.
        """
    @property
    @abstractmethod
    def bounds(self) -> Tuple[BlockCoordinates, BlockCoordinates]:
        """
        The minimum and maximum points in the selection.
        """
    @property
    @abstractmethod
    def bounds_array(self) -> numpy.ndarray:
        """
        The minimum and maximum points in the selection as a numpy array.
        """
    @abstractmethod
    def chunk_boxes(self, sub_chunk_size: int = ...) -> Iterable[Tuple[ChunkCoordinates, SelectionBox]]:
        """
        An iterable of chunk coordinates and boxes that intersect the selection and the chunk.

        >>> for (cx, cz), box in selection1.chunk_boxes():
        >>>     ...

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
    @abstractmethod
    def chunk_count(self, sub_chunk_size: int = ...) -> int:
        """
        The number of chunks that intersect the selection.

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
    @abstractmethod
    def chunk_locations(self, sub_chunk_size: int = ...) -> Iterable[ChunkCoordinates]:
        """
        An iterable of chunk coordinates that intersect the selection.

        >>> for cx, cz in selection1.chunk_locations():
        >>>     ...

        :param sub_chunk_size:  The dimension of a sub-chunk. Default 16.
        """
    @abstractmethod
    def contains_block(self, coords: CoordinatesAny) -> bool:
        """
        Is the block contained within the selection.

        >>> (1, 2, 3) in selection1
        True

        :param coords: The coordinate of the block defined by the most negative corner.
        :return: True if the block is in the selection.
        """
    @abstractmethod
    def contains_point(self, coords: CoordinatesAny) -> bool:
        """
        Is the point contained within the selection.

        >>> (1.5, 2.5, 3.5) in selection1
        True

        :param coords: The coordinate of the point.
        :return: True if the point is in the selection.
        """
    @abstractmethod
    def intersection(self, other):
        """
        Create and return a new a selection containing the volume that this selection and other both contain.

        If the selections do not intersect the returned selection will have no volume.

        Use :meth:`intersects` to test if the two selections intersect.

        :param other: The other selection.
        :return: A new selection containing the intersection.
        """
    @abstractmethod
    def intersects(self, other) -> bool:
        """
        Does this selection intersect ``other``.

        :param other: The other selection.
        :return: True if the selections intersect, False otherwise.
        """
    @property
    @abstractmethod
    def max(self) -> BlockCoordinates:
        """
        The maximum point in the selection.
        """
    @property
    @abstractmethod
    def max_array(self) -> numpy.ndarray:
        """
        The maximum point in the selection as a numpy array.
        """
    @property
    @abstractmethod
    def max_x(self) -> int:
        """
        The maximum x coordinate of the selection.
        """
    @property
    @abstractmethod
    def max_y(self) -> int:
        """
        The maximum y coordinate of the selection.
        """
    @property
    @abstractmethod
    def max_z(self) -> int:
        """
        The maximum z coordinate of the selection.
        """
    @property
    @abstractmethod
    def min(self) -> BlockCoordinates:
        """
        The minimum point in the selection.
        """
    @property
    @abstractmethod
    def min_array(self) -> numpy.ndarray:
        """
        The minimum point in the selection as a numpy array.
        """
    @property
    @abstractmethod
    def min_x(self) -> int:
        """
        The minimum x coordinate of the selection.
        """
    @property
    @abstractmethod
    def min_y(self) -> int:
        """
        The minimum y coordinate of the selection.
        """
    @property
    @abstractmethod
    def min_z(self) -> int:
        """
        The minimum z coordinate of the selection.
        """
    @abstractmethod
    def sub_chunk_boxes(self, sub_chunk_size: int = ...) -> Iterable[Tuple[SubChunkCoordinates, SelectionBox]]:
        """
        An iterable of sub-chunk coordinates and boxes that intersect the selection and the sub-chunk.

        >>> for (cx, cy, cz), box in selection1.sub_chunk_boxes():
        >>>     ...

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
    @abstractmethod
    def sub_chunk_count(self, sub_chunk_size: int = ...) -> int:
        """
        The number of sub-chunks that intersect the selection.

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
    @abstractmethod
    def sub_chunk_locations(self, sub_chunk_size: int = ...) -> Iterable[SubChunkCoordinates]:
        """
        An iterable of sub-chunk coordinates that intersect the selection.

        >>> for cx, cy, cz in selection1.sub_chunk_locations():
        >>>     ...

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """
    @abstractmethod
    def subtract(self, other): ...
    @abstractmethod
    def transform(self, scale: FloatTriplet, rotation: FloatTriplet, translation: FloatTriplet): ...
    @property
    @abstractmethod
    def volume(self) -> int:
        """
        The number of blocks in the selection.
        """
