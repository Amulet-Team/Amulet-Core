from __future__ import annotations
from typing import Any, overload, Self, Callable, TypeVar
from threading import Lock
from collections.abc import Sequence, Hashable
from abc import ABC, abstractmethod

from amulet.version import VersionRange, VersionRangeContainer


T = TypeVar("T", bound=Hashable)


class Palette(VersionRangeContainer, Sequence[T], ABC):
    def __init__(self, version_range: VersionRange) -> None:
        super().__init__(version_range)
        self._lock = Lock()
        self._index_to_item: list[T] = []
        self._item_to_index: dict[T, int] = {}

    def __getstate__(self) -> tuple[Any, ...]:
        return (
            *super().__getstate__(),
            self._index_to_item,
        )

    def __setstate__(self, state: tuple[Any, ...]) -> tuple[Any, ...]:
        self._index_to_item, *state = super().__setstate__(state)
        self._item_to_index = {
            item: index for index, item in enumerate(self._index_to_item)
        }
        return state

    def __len__(self) -> int:
        """
        The number of items in the palette.

        >>> palette: Palette
        >>> len(palette)
        10
        """
        return len(self._index_to_item)

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[T]: ...

    def __getitem__(self, item: int | slice) -> T | Sequence[T]:
        return self._index_to_item[item]

    def __contains__(self, item: Any) -> bool:
        """
        Is the given item already in the palette.

        >>> palette: Palette
        >>> item: T
        >>> item in palette
        True
        >>> 7 in palette
        True

        :param item: The biome or id to check.
        """
        if isinstance(item, int):
            return item < len(self._index_to_item)
        elif self._is_item(item):
            return item in self._item_to_index
        return False

    @abstractmethod
    def _is_item(self, item: T) -> bool:
        raise NotImplementedError

    def _get_index(self, item: T) -> int:
        if item not in self._item_to_index:
            with self._lock:
                if item not in self._item_to_index:
                    self._index_to_item.append(item)
                    self._item_to_index[item] = len(self._index_to_item) - 1
        return self._item_to_index[item]
