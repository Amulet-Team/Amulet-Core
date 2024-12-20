from __future__ import annotations

import collections.abc
import typing

import amulet.selection.box

__all__ = ["SelectionGroup"]

class SelectionGroup:
    """
    A container for zero or more :class:`SelectionBox` instances.

    This allows for non-rectangular and non-contiguous selections.
    """

    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, box: amulet.selection.box.SelectionBox) -> None: ...
    @typing.overload
    def __init__(
        self, boxes: collections.abc.Iterable[amulet.selection.box.SelectionBox]
    ) -> None: ...
    def __repr__(self) -> str: ...
