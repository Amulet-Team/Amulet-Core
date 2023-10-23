from __future__ import annotations
from typing import Union, Iterable
from threading import Lock

from amulet.api.data_types import BiomeType


class BiomePalette:
    """
    Class to handle the mappings between biome strings and their index-based internal IDs
    """

    def __init__(self, biomes: Iterable[BiomeType] = ()):
        """
        Creates a new BiomeManager object
        """
        self._lock = Lock()
        self._index_to_biome: list[BiomeType] = []
        self._biome_to_index: dict[BiomeType, int] = {}

        for biome in biomes:
            self.biome_to_index(biome)

    def __len__(self):
        """
        The number of biomes in the registry.

        >>> biome_palette: BiomePalette
        >>> len(biome_palette)
        10
        """
        return len(self._index_to_biome)

    def __contains__(self, item: Union[int, BiomeType]):
        """
        Is the given biome string already in the registry.

        >>> biome_palette: BiomePalette
        >>> biome_string: BiomeType
        >>> biome_string in biome_palette
        True
        >>> 7 in biome_palette
        True

        :param item: The biome or id to check.
        """
        if isinstance(item, int):
            return item < len(self._index_to_biome)
        elif isinstance(item, BiomeType):
            return item in self._biome_to_index
        return False

    def __iter__(self) -> Iterable[BiomeType]:
        """
        Iterate through all biomes in the registry.

        >>> biome_palette: BiomePalette
        >>> for biome in biome_palette:
        >>>     ...
        """
        yield from self._index_to_biome

    def index_to_biome(self, index: int) -> BiomeType:
        """
        Get the biome at the specified palette index.
        :param index: The index to get
        :return: The biome at that index
        :raises KeyError if there is no biome at that index.
        """
        return self._index_to_biome[index]

    def biome_to_index(self, biome: BiomeType) -> int:
        """
        Get the index of the biome in the palette.
        If it is not in the palette already it will be added first.
        :param biome: The biome to get the index of.
        :return: The index of the biome in the palette.
        """
        if not isinstance(biome, BiomeType):
            raise TypeError(repr(biome))
        if biome not in self._biome_to_index:
            with self._lock:
                if biome not in self._biome_to_index:
                    self._index_to_biome.append(biome)
                    self._biome_to_index[biome] = len(self._index_to_biome) - 1
        return self._biome_to_index[biome]
