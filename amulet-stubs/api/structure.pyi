from _typeshed import Incomplete
from amulet.api.data_types import Dimension as Dimension
from amulet.api.level import BaseLevel as BaseLevel
from typing import Tuple

class StructureCache:
    """A class for storing and accessing structure objects"""
    _structure_buffer: Incomplete
    def __init__(self) -> None: ...
    def add_structure(self, structure: BaseLevel, dimension: Dimension):
        """Add a structure to the cache"""
    def get_structure(self, index: int = ...) -> Tuple[BaseLevel, Dimension]:
        """Get a structure from the cache. Default last."""
    def pop_structure(self, index: int = ...) -> Tuple[BaseLevel, Dimension]:
        """Get and remove a structure from the cache. Default last."""
    def __len__(self) -> int:
        """Get the number of structures in the cache"""
    def clear(self) -> None:
        """Empty the cache."""

structure_cache: Incomplete
