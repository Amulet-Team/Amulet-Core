from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

from amulet.api.data_types import BiomeType
from amulet.api.block import Block
from amulet.api.selection import SelectionGroup

from ._level import LevelFriend

if TYPE_CHECKING:
    from ._chunk_storage import ChunkStorage


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
    def chunk(self) -> ChunkStorage:
        """Methods to interact with the chunk data for the level."""
        raise NotImplementedError
