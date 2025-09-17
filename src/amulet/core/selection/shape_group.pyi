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
    def deserialise(s: str) -> SelectionShapeGroup: ...
    def __bool__(self) -> bool:
        """
        Are there any selections in the group.
        """

    def __contains__(self, item: typing.Any) -> bool: ...
    def __copy__(self) -> SelectionShapeGroup: ...
    def __deepcopy__(self, memo: dict) -> SelectionShapeGroup: ...
    def __delitem__(self, index: typing.SupportsInt) -> None: ...
    @typing.overload
    def __eq__(self, other: SelectionShapeGroup) -> bool: ...
    @typing.overload
    def __eq__(self, other: typing.Any) -> bool | types.NotImplementedType: ...
    @typing.overload
    def __getitem__(
        self, index: typing.SupportsInt
    ) -> amulet.core.selection.shape.SelectionShape: ...
    @typing.overload
    def __getitem__(
        self, item: slice
    ) -> list[amulet.core.selection.shape.SelectionShape]: ...
    def __iadd__(
        self,
        values: collections.abc.Iterable[amulet.core.selection.shape.SelectionShape],
    ) -> typing.Any: ...
    @typing.overload
    def __init__(self) -> None:
        """
        Create an empty SelectionShapeGroup.

        >>> SelectionShapeGroup()
        """

    @typing.overload
    def __init__(
        self, box_group: amulet.core.selection.box_group.SelectionBoxGroup
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
    ) -> collections.abc.Iterator[amulet.core.selection.shape.SelectionShape]: ...
    def __len__(self) -> int:
        """
        The number of :class:`SelectionShape` classes in the group.
        """

    def __repr__(self) -> str: ...
    def __reversed__(
        self,
    ) -> collections.abc.Iterator[amulet.core.selection.shape.SelectionShape]: ...
    def __setitem__(
        self,
        index: typing.SupportsInt,
        item: amulet.core.selection.shape.SelectionShape,
    ) -> None: ...
    def almost_equal(self, other: SelectionShapeGroup) -> bool:
        """
        Returns True of the shape groups are equal or almost equal.
        """

    def append(self, value: amulet.core.selection.shape.SelectionShape) -> None: ...
    def clear(self) -> None: ...
    def count(self, value: amulet.core.selection.shape.SelectionShape) -> int: ...
    def extend(
        self,
        values: collections.abc.Iterable[amulet.core.selection.shape.SelectionShape],
    ) -> None: ...
    def index(
        self,
        value: amulet.core.selection.shape.SelectionShape,
        start: typing.SupportsInt = 0,
        stop: typing.SupportsInt = 9223372036854775807,
    ) -> int: ...
    def insert(
        self,
        index: typing.SupportsInt,
        item: amulet.core.selection.shape.SelectionShape,
    ) -> None: ...
    def pop(self, index: typing.SupportsInt = -1) -> typing.Any: ...
    def remove(self, value: amulet.core.selection.shape.SelectionShape) -> None: ...
    def reverse(self) -> None: ...
    def serialise(self) -> str: ...
    def voxelise(self) -> amulet.core.selection.box_group.SelectionBoxGroup:
        """
        Convert the shapes to a SelectionBoxGroup.
        """
