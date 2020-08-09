from typing import Dict, overload, List, Union

from amulet.api.data_types import Int


class BiomeManager:
    def __init__(self):
        self._to_str: List[str] = []
        self._to_int: Dict[str, int] = {}
        self._item_count = 0

    def get_add_biome(self, biome: str) -> int:
        """Register the biome and get the runtime id."""
        assert isinstance(biome, str), f"biome must be a string. Got {biome}"
        if biome not in self._to_int:
            self._to_int[biome] = len(self._to_str)
            self._to_str.append(biome)
        return self._to_int[biome]

    def __contains__(self, item: Union[int, str]):
        if isinstance(item, int):
            return item < len(self._to_str)
        elif isinstance(item, str):
            return item in self._to_int
        return False

    @overload
    def __getitem__(self, item: str) -> int:
        ...

    @overload
    def __getitem__(self, item: Int) -> str:
        ...

    def __getitem__(self, item):
        """
        If a string is passed to this function, it will return the internal ID/index of the biome.
        If an int is given, this method will return the biome string at that specified index.
        If the key is not present KeyError will be raised.

        :param item: The string or int to get the mapping data of
        :return: An int if a string was supplied, a string if an int was supplied
        """
        try:
            if isinstance(item, str):
                return self._to_int[item]
            return self._to_str[item]

        except (KeyError, IndexError):
            raise KeyError(
                f"There is no {item} in the BiomeManager. "
                f"You might want to use the `get_add_biome` function for the biome before accessing them."
            )
