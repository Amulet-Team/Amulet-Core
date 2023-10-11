from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

from amulet.api.data_types import BiomeType
from amulet.api.block import Block
from amulet.api.selection import SelectionGroup

from ._namespaces.namespace import LevelFriend

if TYPE_CHECKING:
    from ._namespaces.chunk import ChunkNamespace


class DimensionCls(LevelFriend, ABC):
    @abstractmethod
    def bounds(self) -> SelectionGroup:
        """The editable region of the dimension."""
        raise NotImplementedError

    @abstractmethod
    def default_block(self) -> Block:
        """The default block for this dimension"""
        raise NotImplementedError

    @abstractmethod
    def default_biome(self) -> BiomeType:
        """The default biome for this dimension"""
        raise NotImplementedError

    @property
    @abstractmethod
    def chunk(self) -> ChunkNamespace:
        """Methods to interact with the chunk data for the level."""
        raise NotImplementedError
