from __future__ import annotations

import types
import typing

import amulet.core.selection.box_group
import amulet.utils.matrix

__all__: list[str] = ["SelectionBox"]

class SelectionBox:
    """
    The SelectionBox class represents a single cuboid selection.

    When combined with :class:`~amulet.api.selection.SelectionBoxGroup` it can represent any arbitrary shape.
    """

    @typing.overload
    def __eq__(self, other: SelectionBox) -> bool: ...
    @typing.overload
    def __eq__(self, other: typing.Any) -> bool | types.NotImplementedType: ...
    def __ge__(self, arg0: SelectionBox) -> bool: ...
    def __gt__(self, arg0: SelectionBox) -> bool: ...
    def __hash__(self) -> int: ...
    @typing.overload
    def __init__(
        self,
        min_x: typing.SupportsInt,
        min_y: typing.SupportsInt,
        min_z: typing.SupportsInt,
        size_x: typing.SupportsInt,
        size_y: typing.SupportsInt,
        size_z: typing.SupportsInt,
    ) -> None:
        """
        Construct a new SelectionBox instance.

        >>> # a selection box that selects one block.
        >>> box = SelectionBox(0, 0, 0, 1, 1, 1)

        :param min_x: The minimum x coordinate of the box.
        :param min_y: The minimum y coordinate of the box.
        :param min_z: The minimum z coordinate of the box.
        :param size_x: The size of the box in the x axis.
        :param size_y: The size of the box in the y axis.
        :param size_z: The size of the box in the z axis.
        """

    @typing.overload
    def __init__(
        self,
        point_1: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt],
        point_2: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt],
    ) -> None:
        """
        Construct a new SelectionBox instance.

        >>> # a selection box that selects one block.
        >>> box = SelectionBox((0, 0, 0), (1, 1, 1))

        :param point_1: The first coordinate of the box.
        :param point_2: The second coordinate of the box.
        """

    def __le__(self, arg0: SelectionBox) -> bool: ...
    def __lt__(self, arg0: SelectionBox) -> bool: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def contains_block(
        self, x: typing.SupportsInt, y: typing.SupportsInt, z: typing.SupportsInt
    ) -> bool:
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

    def contains_box(self, other: SelectionBox) -> bool:
        """
        Does the other SelectionBox other fit entirely within this SelectionBox.

        :param other: The SelectionBox to test.
        :return: True if other fits in self, False otherwise.
        """

    def contains_point(
        self, x: typing.SupportsFloat, y: typing.SupportsFloat, z: typing.SupportsFloat
    ) -> bool:
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

    @typing.overload
    def intersects(self, other: SelectionBox) -> bool:
        """
        Does this selection intersect ``other``.

        :param other: The other selection.
        :return: True if the selections intersect, False otherwise.
        """

    @typing.overload
    def intersects(
        self, other: amulet.core.selection.box_group.SelectionBoxGroup
    ) -> bool: ...
    def touches(self, other: SelectionBox) -> bool:
        """
        Method to check if this instance of :class:`SelectionBox` touches but does not intersect another SelectionBox.

        :param other: The other SelectionBox
        :return: True if the two :class:`SelectionBox` instances touch, False otherwise
        """

    def touches_or_intersects(self, other: SelectionBox) -> bool:
        """
        Does this SelectionBox touch or intersect the other SelectionBox.

        :param other: The other SelectionBox.
        :return: True if the two :class:`SelectionBox` instances touch or intersect, False otherwise.
        """

    def transform(
        self, matrix: amulet.utils.matrix.Matrix4x4
    ) -> amulet.core.selection.box_group.SelectionBoxGroup:
        """
        Transform this box by the given transformation matrix.
        """

    def translate(
        self, dx: typing.SupportsInt, dy: typing.SupportsInt, dz: typing.SupportsInt
    ) -> SelectionBox:
        """
        Create a new :class:`SelectionBox` based on this one with the coordinates moved by the given offset.

        :param dx: The x offset.
        :param dy: The y offset.
        :param dz: The z offset.
        :return: The new selection with the given offset.
        """

    @property
    def max(self) -> tuple[int, int, int]:
        """
        The maximum coordinate of the box.
        """

    @property
    def max_x(self) -> int:
        """
        The maximum x coordinate of the box.
        """

    @property
    def max_y(self) -> int:
        """
        The maximum y coordinate of the box.
        """

    @property
    def max_z(self) -> int:
        """
        The maximum z coordinate of the box.
        """

    @property
    def min(self) -> tuple[int, int, int]:
        """
        The minimum coordinate of the box.
        """

    @property
    def min_x(self) -> int:
        """
        The minimum x coordinate of the box.
        """

    @property
    def min_y(self) -> int:
        """
        The minimum y coordinate of the box.
        """

    @property
    def min_z(self) -> int:
        """
        The minimum z coordinate of the box.
        """

    @property
    def shape(self) -> tuple[int, int, int]:
        """
        The length of the box in the x, y and z axis.

        >>> SelectionBox(0, 0, 0, 1, 1, 1).shape
        (1, 1, 1)
        """

    @property
    def size_x(self) -> int:
        """
        The length of the box in the x axis.
        """

    @property
    def size_y(self) -> int:
        """
        The length of the box in the y axis.
        """

    @property
    def size_z(self) -> int:
        """
        The length of the box in the z axis.
        """

    @property
    def volume(self) -> int:
        """
        The number of blocks in the box.

        >>> SelectionBox(0, 0, 0, 1, 1, 1).volume
        1
        """
