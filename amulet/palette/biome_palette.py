from __future__ import annotations
from typing import Any, overload, Self, Callable
from threading import Lock
from collections.abc import Sequence

from amulet.biome import Biome
from amulet.version import VersionRange, VersionRangeContainer


class BiomePalette(VersionRangeContainer, Sequence[Biome]):
    """
    Class to handle the mappings between biomes and their index-based internal IDs
    """

    def __init__(self, version_range: VersionRange) -> None:
        """
        Creates a new BiomeManager object
        """
        super().__init__(version_range)
        self._lock = Lock()
        self._index_to_biome: list[Biome] = []
        self._biome_to_index: dict[Biome, int] = {}

    @classmethod
    def _reconstruct(
        cls,
        version_range: VersionRange,
        index_to_biome: list[Biome],
        biome_to_index: dict[Biome, int],
    ) -> Self:
        self = cls(version_range)
        self._index_to_biome = index_to_biome
        self._biome_to_index = biome_to_index
        return self

    def __reduce__(
        self,
    ) -> tuple[
        Callable[[VersionRange, list[Biome], dict[Biome, int]], Self],
        tuple[VersionRange, list[Biome], dict[Biome, int]],
    ]:
        return self._reconstruct, (
            self.version_range,
            self._index_to_biome,
            self._biome_to_index,
        )

    def __len__(self) -> int:
        """
        The number of biomes in the palette.

        >>> biome_palette: BiomePalette
        >>> len(biome_palette)
        10
        """
        return len(self._index_to_biome)

    @overload
    def __getitem__(self, index: int) -> Biome:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Biome]:
        ...

    def __getitem__(self, item: int | slice) -> Biome | Sequence[Biome]:
        return self._index_to_biome[item]

    def __contains__(self, item: Any) -> bool:
        """
        Is the given biome already in the palette.

        >>> biome_palette: BiomePalette
        >>> biome: Biome
        >>> biome in biome_palette
        True
        >>> 7 in biome_palette
        True

        :param item: The biome or id to check.
        """
        if isinstance(item, int):
            return item < len(self._index_to_biome)
        elif isinstance(item, Biome):
            return item in self._biome_to_index
        return False

    def index_to_biome(self, index: int) -> Biome:
        """
        Get the biome at the specified palette index.
        :param index: The index to get
        :return: The biome at that index
        :raises KeyError if there is no biome at that index.
        """
        return self._index_to_biome[index]

    def biome_to_index(self, biome: Biome) -> int:
        """
        Get the index of the biome in the palette.
        If it is not in the palette already it will be added first.
        :param biome: The biome to get the index of.
        :return: The index of the biome in the palette.
        """
        if not isinstance(biome, Biome):
            raise TypeError(repr(biome))
        if biome.version not in self.version_range:
            raise ValueError(f"Biome {biome} is incompatible with {self.version_range}")
        if biome not in self._biome_to_index:
            with self._lock:
                if biome not in self._biome_to_index:
                    self._index_to_biome.append(biome)
                    self._biome_to_index[biome] = len(self._index_to_biome) - 1
        return self._biome_to_index[biome]
