from __future__ import annotations

from amulet.biome import Biome
from ._palette import Palette


class BiomePalette(Palette[Biome]):
    """
    Class to handle the mappings between biomes and their index-based internal IDs
    """

    def _is_item(self, item: Biome) -> bool:
        return isinstance(item, Biome)

    def index_to_biome(self, index: int) -> Biome:
        """
        Get the biome at the specified palette index.
        :param index: The index to get
        :return: The biome at that index
        :raises KeyError if there is no biome at that index.
        """
        return self._index_to_item[index]

    def biome_to_index(self, biome: Biome) -> int:
        """
        Get the index of the biome in the palette.
        If it is not in the palette already it will be added first.
        :param biome: The biome to get the index of.
        :return: The index of the biome in the palette.
        """
        if not isinstance(biome, Biome):
            raise TypeError(repr(biome))
        if not self.version_range.contains(biome.platform, biome.version):
            raise ValueError(f"Biome {biome} is incompatible with {self.version_range}")
        return self._get_index(biome)

    def __repr__(self) -> str:
        return f"BiomePalette({self.version_range!r}) # {len(self)} biomes"
