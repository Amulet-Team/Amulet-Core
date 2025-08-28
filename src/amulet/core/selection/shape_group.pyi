from __future__ import annotations

import collections.abc
import typing

import amulet.core.selection.shape

__all__: list[str] = ["SelectionShapeGroup"]

class SelectionShapeGroup:
    """
    A group of selection shapes.
    """

    def __bool__(self) -> bool:
        """
        Are there any selections in the group.
        """

    @typing.overload
    def __init__(self) -> None:
        """
        Create an empty SelectionShapeGroup.

        >>> SelectionShapeGroup()
        """

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

    @property
    def shapes(
        self,
    ) -> collections.abc.Iterator[amulet.core.selection.shape.SelectionShape]:
        """
        An iterator of the :class:`SelectionShape` instances stored for this group.
        """
