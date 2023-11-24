from typing import TypeVar
from collections.abc import Mapping, Iterator

K = TypeVar("K")
V = TypeVar("V")


class FrozenMapping(Mapping[K, V]):
    """
    A hashable Mapping class.
    All values in the mapping must be hashable.
    """

    def __init__(self, mapping: Mapping):
        self._map = dict(mapping)
        self._hash = hash(frozenset(self._map.items()))

    def __getitem__(self, k: K) -> V:
        return self._map[k]

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[K]:
        return iter(self._map)

    def __hash__(self):
        return self._hash
