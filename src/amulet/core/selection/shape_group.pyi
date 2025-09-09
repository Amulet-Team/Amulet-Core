from __future__ import annotations

import collections.abc
import types
import typing

import amulet.core.selection.box_group
import amulet.core.selection.shape

__all__: list[str] = ["SelectionShapeGroup"]

class SelectionShapeGroup:
    """
    A group of selection shapes.
    """

    __hash__: typing.ClassVar[None] = None  # type: ignore
    @staticmethod
    def deserialise(arg0: str) -> SelectionShapeGroup: ...
    def __bool__(self) -> bool:
        """
        Are there any selections in the group.
        """

    def __copy__(self) -> SelectionShapeGroup: ...
    def __deepcopy__(self, memo: dict) -> SelectionShapeGroup: ...
    def __delitem__(self, arg0: typing.SupportsInt) -> None: ...
    @typing.overload
    def __eq__(self, arg0: SelectionShapeGroup) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: typing.Any) -> bool | types.NotImplementedType: ...
    def __getitem__(
        self, arg0: typing.SupportsInt
    ) -> amulet.core.selection.shape.SelectionShape: ...
    @typing.overload
    def __init__(self) -> None:
        """
        Create an empty SelectionShapeGroup.

        >>> SelectionShapeGroup()
        """

    @typing.overload
    def __init__(
        self, arg0: amulet.core.selection.box_group.SelectionBoxGroup
    ) -> None: ...
    @typing.overload
    def __init__(
        self,
        shapes: collections.abc.Iterable[amulet.core.selection.shape.SelectionShape],
    ) -> None:
        """
        Create a SelectionShapeGroup from the selections in the iterable.

        >>> SelectionShapeGroup([
        >>>     SelectionCuboid(0, 0, 0, 5, 5, 5),
        >>>     SelectionEllipsoid(7.5, 0, 0, 2.5)
        >>> ])
        """

    def __iter__(
        self,
    ) -> collections.abc.Iterator[amulet.core.selection.shape.SelectionShape]:
        """
        An iterable of all the :class:`SelectionShape` classes in the group.
        """

    def __len__(self) -> int:
        """
        The number of :class:`SelectionShape` classes in the group.
        """

    def __repr__(self) -> str: ...
    def __setitem__(
        self,
        index: typing.SupportsInt,
        item: amulet.core.selection.shape.SelectionShape,
    ) -> None: ...
    def almost_equal(self, other: SelectionShapeGroup) -> bool:
        """
        Returns True of the shape groups are equal or almost equal.
        """

    def insert(
        self, arg0: typing.SupportsInt, arg1: amulet.core.selection.shape.SelectionShape
    ) -> None: ...
    def serialise(self) -> str: ...
    def voxelise(self) -> amulet.core.selection.box_group.SelectionBoxGroup:
        """
        Convert the shapes to a SelectionBoxGroup.
        """

    @property
    def shapes(
        self,
    ) -> collections.abc.Iterator[amulet.core.selection.shape.SelectionShape]:
        """
        An iterator of the :class:`SelectionShape` instances stored for this group.
        """
