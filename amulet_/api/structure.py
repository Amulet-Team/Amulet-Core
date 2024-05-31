from typing import List, Tuple

from amulet.api.level import BaseLevel
from amulet.api.data_types import Dimension


class StructureCache:
    """A class for storing and accessing structure objects"""

    def __init__(self):
        self._structure_buffer: List[Tuple[BaseLevel, Dimension]] = []

    def add_structure(self, structure: BaseLevel, dimension: Dimension):
        """Add a structure to the cache"""
        assert isinstance(
            structure, BaseLevel
        ), "structure given is not a BaseLevel instance"
        self._structure_buffer.append((structure, dimension))

    def get_structure(self, index=-1) -> Tuple[BaseLevel, Dimension]:
        """Get a structure from the cache. Default last."""
        return self._structure_buffer[index]

    def pop_structure(self, index=-1) -> Tuple[BaseLevel, Dimension]:
        """Get and remove a structure from the cache. Default last."""
        return self._structure_buffer.pop(index)

    def __len__(self) -> int:
        """Get the number of structures in the cache"""
        return len(self._structure_buffer)

    def clear(self):
        """Empty the cache."""
        self._structure_buffer.clear()


structure_cache = StructureCache()
