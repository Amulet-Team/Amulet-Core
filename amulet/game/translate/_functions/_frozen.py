from typing import TypeVar, Any
from collections.abc import Mapping, Iterator, Hashable, Set, Iterable

K = TypeVar("K", bound=Hashable)
V = TypeVar("V", bound=Hashable)


class FrozenMapping(Mapping[K, V], Hashable):
    """
    A hashable Mapping class.
    All values in the mapping must be hashable.
    """

    _map: Mapping[K, V]
    _h: int | None

    def __init__(self, mapping: Mapping) -> None:
        self._map: dict[K, V] = dict(mapping)
        self._h = None

    def __getitem__(self, k: K) -> V:
        return self._map[k]

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[K]:
        return iter(self._map)

    def __hash__(self) -> int:
        if self._h is None:
            self._h = hash(frozenset(self._map.items()))
        return self._h

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Mapping):
            return NotImplemented
        return self._map == other


class OrderedFrozenSet(Set[K], Hashable):
    _map: dict[K, None]
    _h: int | None

    def __init__(self, items: Iterable[K]) -> None:
        self._map = dict.fromkeys(items)
        self._h = None

    def __contains__(self, item: Any) -> bool:
        return item in self._map

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[K]:
        yield from self._map

    def __hash__(self) -> int:
        if self._h is None:
            self._h = hash(tuple(self._map))
        return self._h

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Set):
            return NotImplemented
        return self._map.keys() == other
