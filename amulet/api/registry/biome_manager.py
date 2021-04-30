from typing import Dict, overload, List, Union, Tuple, Generator, Iterable

from amulet.api.data_types import Int, BiomeType
from amulet.api.registry.base_registry import BaseRegistry


class BiomeManager(BaseRegistry):
    """
    Class to handle the mappings between biome strings and their index-based internal IDs
    """

    def __init__(self, biomes: Iterable[BiomeType] = ()):
        """
        Creates a new BiomeManager object
        """
        self._index_to_biome: List[BiomeType] = []
        self._biome_to_index: Dict[BiomeType, int] = {}
        for biome in biomes:
            # if a list is given it is assumed that the block palette will be the same size as the list.
            # Ensure that if a value is duplicated it will appear twice in the list
            assert isinstance(biome, str), f"biome must be a string. Got {biome}"
            if biome not in self._biome_to_index:
                self._biome_to_index[biome] = len(self._index_to_biome)
            self._index_to_biome.append(biome)

    def __len__(self):
        """
        The number of biomes in the registry.

        >>> len(level.biome_palette)
        10
        """
        return len(self._index_to_biome)

    def __contains__(self, item: Union[int, BiomeType]):
        """
        Is the given biome string already in the registry.

        >>> biome_string in level.biome_palette
        True
        >>> 7 in level.biome_palette
        True

        :param item: The biome or id to check.
        """
        if isinstance(item, int):
            return item < len(self._index_to_biome)
        elif isinstance(item, str):
            return item in self._biome_to_index
        return False

    def __iter__(self) -> Iterable[BiomeType]:
        """
        Iterate through all biomes in the registry.

        >>> for biome in level.biome_palette:
        >>>     ...
        """
        yield from self._index_to_biome

    def biomes(self) -> Tuple[BiomeType]:
        """
        The biomes in the registry as a tuple.
        """
        return tuple(self._index_to_biome)

    def values(self) -> Tuple[BiomeType]:
        """
        The biomes in the registry as a tuple.
        """
        return self.biomes()

    def items(self) -> Generator[Tuple[int, BiomeType], None, None]:
        """
        A generator of the biome indexes and the biome strings.
        """
        yield from enumerate(self._index_to_biome)

    @overload
    def __getitem__(self, item: BiomeType) -> int:
        ...

    @overload
    def __getitem__(self, item: Int) -> BiomeType:
        ...

    def __getitem__(self, item):
        """
        If a string is passed to this function, it will return the internal ID/index of the biome.

        If an int is given, this method will return the biome string at that specified index.

        :param item: The string or int to get the mapping data of
        :return: An int if a string was supplied, a string if an int was supplied
        :raises KeyError if the requested item is not present.
        """
        try:
            if isinstance(item, str):
                return self._biome_to_index[item]
            return self._index_to_biome[item]

        except (KeyError, IndexError):
            raise KeyError(
                f"There is no {item} in the BiomeManager. "
                f"You might want to use the `get_add_biome` function for the biome before accessing them."
            )

    def get_add_biome(self, biome: BiomeType) -> int:
        """
        Adds a biome string to the internal biome string/ID mappings.

        If the biome already exists in the mappings, the existing ID is returned.

        :param biome: The biome string to add to the manager
        :return: The internal ID of the biome
        """
        assert isinstance(biome, str), f"biome must be a string. Got {biome}"
        if biome not in self._biome_to_index:
            self._biome_to_index[biome] = len(self._index_to_biome)
            self._index_to_biome.append(biome)
        return self._biome_to_index[biome]

    def register(self, biome: BiomeType) -> int:
        """
        An alias of :meth:`get_add_biome`.

        Adds a biome string to the internal biome string/ID mappings.

        If the biome already exists in the mappings, the existing ID is returned.

        :param biome: The biome string to add to the manager
        :return: The internal ID of the biome
        """
        return self.get_add_biome(biome)
