from _typeshed import Incomplete
from amulet.biome import Biome as Biome
from amulet.version import VersionRange as VersionRange, VersionRangeContainer as VersionRangeContainer
from collections.abc import Sequence
from typing import Union

class BiomePalette(VersionRangeContainer, Sequence[Biome]):
    """
    Class to handle the mappings between biomes and their index-based internal IDs
    """
    _lock: Incomplete
    _index_to_biome: Incomplete
    _biome_to_index: Incomplete
    def __init__(self, version_range: VersionRange) -> None:
        """
        Creates a new BiomeManager object
        """
    def __len__(self) -> int:
        """
        The number of biomes in the palette.

        >>> biome_palette: BiomePalette
        >>> len(biome_palette)
        10
        """
    def __getitem__(self, item): ...
    def __contains__(self, item: Union[int, Biome]) -> bool:
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
    def index_to_biome(self, index: int) -> Biome:
        """
        Get the biome at the specified palette index.
        :param index: The index to get
        :return: The biome at that index
        :raises KeyError if there is no biome at that index.
        """
    def biome_to_index(self, biome: Biome) -> int:
        """
        Get the index of the biome in the palette.
        If it is not in the palette already it will be added first.
        :param biome: The biome to get the index of.
        :return: The index of the biome in the palette.
        """
