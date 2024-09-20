from typing import Any, Iterable, Iterator, TypeAlias, overload

import numpy
from amulet import selection as selection
from amulet.data_types import BlockCoordinates as BlockCoordinates
from amulet.data_types import BlockCoordinatesArray as BlockCoordinatesArray
from amulet.data_types import ChunkCoordinates as ChunkCoordinates
from amulet.data_types import FloatTriplet as FloatTriplet
from amulet.data_types import PointCoordinates as PointCoordinates
from amulet.data_types import PointCoordinatesArray as PointCoordinatesArray
from amulet.data_types import SubChunkCoordinates as SubChunkCoordinates
from amulet.utils.matrix import displacement_matrix as displacement_matrix
from amulet.utils.matrix import transform_matrix as transform_matrix
from amulet.utils.world_utils import (
    block_coords_to_chunk_coords as block_coords_to_chunk_coords,
)
from amulet.utils.world_utils import (
    blocks_slice_to_chunk_slice as blocks_slice_to_chunk_slice,
)

from .abstract_selection import AbstractBaseSelection as AbstractBaseSelection
from .group import SelectionGroup as SelectionGroup

PySlice: TypeAlias

class SelectionBox(AbstractBaseSelection):
    """
    The SelectionBox class represents a single cuboid selection.

    When combined with :class:`~amulet.api.selection.SelectionGroup` it can represent any arbitrary shape.
    """

    def __init__(
        self,
        point_1: BlockCoordinates | BlockCoordinatesArray,
        point_2: BlockCoordinates | BlockCoordinatesArray,
    ) -> None:
        """
        Construct a new SelectionBox instance.

        >>> # a selection box that selects one block.
        >>> box = SelectionBox(
        >>>     (0, 0, 0),
        >>>     (1, 1, 1)
        >>> )

        :param point_1: The first point of the selection.
        :param point_2: The second point of the selection.
        """

    @classmethod
    def create_chunk_box(
        cls, cx: int, cz: int, sub_chunk_size: int = 16
    ) -> SelectionBox:
        """
        Get a :class:`SelectionBox` containing the whole of a given chunk.

        >>> box = SelectionBox.create_chunk_box(1, 2)
        SelectionBox((16, -1073741824, 32), (32, 1073741824, 48))

        :param cx: The x coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """

    @classmethod
    def create_sub_chunk_box(
        cls, cx: int, cy: int, cz: int, sub_chunk_size: int = 16
    ) -> SelectionBox:
        """
        Get a :class:`SelectionBox` containing the whole of a given sub-chunk.

        >>> SelectionBox.create_sub_chunk_box(1, 0, 2)
        SelectionBox((16, 0, 32), (32, 16, 48))

        :param cx: The x coordinate of the chunk
        :param cy: The y coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """

    def create_moved_box(
        self, offset: BlockCoordinates | BlockCoordinatesArray, subtract: bool = False
    ) -> SelectionBox:
        """
        Create a new :class:`SelectionBox` based on this one with the coordinates moved by the given offset.

        :param offset: The amount to move the box.
        :param subtract: If true will subtract the offset rather than adding.
        :return: The new selection with the given offset.
        """

    def chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Iterator[ChunkCoordinates]: ...
    def chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterator[tuple[ChunkCoordinates, SelectionBox]]: ...
    def chunk_y_locations(self, sub_chunk_size: int = 16) -> Iterable[int]:
        """
        An iterable of all the sub-chunk y indexes this box intersects.

        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """

    def sub_chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Iterator[SubChunkCoordinates]: ...
    def chunk_count(self, sub_chunk_size: int = 16) -> int: ...
    def sub_chunk_count(self, sub_chunk_size: int = 16) -> int: ...
    def sub_chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterator[tuple[SubChunkCoordinates, SelectionBox]]: ...
    @property
    def blocks(self) -> Iterator[BlockCoordinates]: ...
    def contains_block(self, x: int, y: int, z: int) -> bool: ...
    def contains_point(self, x: float, y: float, z: float) -> bool: ...
    def __eq__(self, other: Any) -> bool: ...
    def __ne__(self, other: Any) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def slice(self) -> tuple[PySlice, PySlice, PySlice]:
        """
        Converts the :class:`SelectionBox` minimum/maximum coordinates into slice arguments

        :return: The :class:`SelectionBox` coordinates as slices in (x,y,z) order
        """

    def chunk_slice(
        self, cx: int, cz: int, sub_chunk_size: int = 16
    ) -> tuple[PySlice, PySlice, PySlice]:
        """
        Get the slice of the box in relative form for a given chunk.

        >>> SelectionBox((0, 0, 0), (32, 32, 32)).chunk_slice(1, 1)
        (slice(0, 16, None), slice(0, 32, None), slice(0, 16, None))

        :param cx: The x coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """

    def sub_chunk_slice(
        self, cx: int, cy: int, cz: int, sub_chunk_size: int = 16
    ) -> tuple[PySlice, PySlice, PySlice]:
        """
        Get the slice of the box in relative form for a given sub-chunk.

        >>> SelectionBox((0, 0, 0), (32, 32, 32)).sub_chunk_slice(1, 1, 1)
        (slice(0, 16, None), slice(0, 16, None), slice(0, 16, None))

        :param cx: The x coordinate of the chunk
        :param cy: The y coordinate of the chunk
        :param cz: The z coordinate of the chunk
        :param sub_chunk_size: The dimension of a sub-chunk. Default 16.
        """

    @property
    def point_1(self) -> BlockCoordinates:
        """The first value given to the constructor."""

    @property
    def point_2(self) -> BlockCoordinates:
        """The second value given to the constructor."""

    @property
    def points(self) -> tuple[BlockCoordinates, BlockCoordinates]:
        """The points given to the constructor."""

    @property
    def points_array(self) -> numpy.ndarray:
        """The points given to the constructor as a numpy array."""

    @property
    def min_x(self) -> int: ...
    @property
    def min_y(self) -> int: ...
    @property
    def min_z(self) -> int: ...
    @property
    def max_x(self) -> int: ...
    @property
    def max_y(self) -> int: ...
    @property
    def max_z(self) -> int: ...
    @property
    def min(self) -> BlockCoordinates: ...
    @property
    def min_array(self) -> numpy.ndarray: ...
    @property
    def max(self) -> BlockCoordinates: ...
    @property
    def max_array(self) -> numpy.ndarray: ...
    @property
    def bounds(self) -> tuple[BlockCoordinates, BlockCoordinates]: ...
    @property
    def bounds_array(self) -> numpy.ndarray: ...
    def bounding_box(self) -> SelectionBox: ...
    def selection_group(self) -> SelectionGroup: ...
    @property
    def size_x(self) -> int:
        """The length of the box in the x axis."""

    @property
    def size_y(self) -> int:
        """The length of the box in the y axis."""

    @property
    def size_z(self) -> int:
        """The length of the box in the z axis."""

    @property
    def shape(self) -> tuple[int, int, int]:
        """
        The shape of the box.

        >>> SelectionBox((0, 0, 0), (1, 1, 1)).shape
        (1, 1, 1)
        """

    @property
    def volume(self) -> int:
        """
        The number of blocks in the box.

        >>> SelectionBox((0, 0, 0), (1, 1, 1)).shape
        1
        """

    def touches(self, other: SelectionBox) -> bool:
        """
        Method to check if this instance of :class:`SelectionBox` touches but does not intersect another SelectionBox.

        :param other: The other SelectionBox
        :return: True if the two :class:`SelectionBox` instances touch, False otherwise
        """

    def touches_or_intersects(self, other: SelectionBox) -> bool:
        """
        Method to check if this instance of SelectionBox touches or intersects another SelectionBox.

        :param other: The other SelectionBox.
        :return: True if the two :class:`SelectionBox` instances touch or intersect, False otherwise.
        """

    def contains_box(self, other: SelectionBox) -> bool:
        """
        Method to check if the other SelectionBox other fits entirely within this instance of SelectionBox.

        :param other: The SelectionBox to test.
        :return: True if other fits with self, False otherwise.
        """

    @overload
    def intersection(self, other: SelectionBox) -> SelectionBox: ...
    @overload
    def intersection(self, other: SelectionGroup) -> SelectionGroup: ...
    @overload
    def intersection(self, other: AbstractBaseSelection) -> AbstractBaseSelection: ...
    def subtract(self, other: AbstractBaseSelection) -> SelectionGroup:
        """
        Get a :class:`~amulet.api.selection.SelectionGroup` containing boxes that are in self but not in other.

        This may be empty if other fully contains self or equal to self if they do not intersect.

        :param other: The SelectionBox to subtract.
        :return:
        """

    def intersects_vector(
        self,
        origin: PointCoordinates | PointCoordinatesArray,
        direction: PointCoordinates | PointCoordinatesArray,
    ) -> float | None:
        """
        Determine if a vector from a given point collides with this selection box.

        :param origin: Location of the origin of the vector
        :param direction: The look vector
        :return: Multiplier of the vector to the collision location. None if it does not collide
        """

    def transformed_points(
        self, transform: numpy.ndarray
    ) -> Iterable[tuple[float, numpy.ndarray | None, numpy.ndarray | None]]:
        """
        Get the locations of the transformed blocks and the source blocks they came from.

        :param transform: The matrix that this box will be transformed by.
        :return: An iterable of two Nx3 numpy arrays of the source block locations and the destination block locations. The destination locations will be unique but the source may not be and some may not be included.
        """

    def transform(
        self, scale: FloatTriplet, rotation: FloatTriplet, translation: FloatTriplet
    ) -> SelectionGroup:
        """
        Creates a :class:`~amulet.api.selection.SelectionGroup` of transformed SelectionBox(es).

        :param scale: A tuple of scaling factors in the x, y and z axis.
        :param rotation: The rotation about the x, y and z axis in radians.
        :param translation: The translation about the x, y and z axis.
        :return: A new :class:`~amulet.api.selection.SelectionGroup` representing the transformed selection.
        """
