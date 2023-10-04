from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence
from amulet.api.data_types import (
    Dimension,
    BiomeType,
)
from amulet.api.selection import SelectionGroup
from amulet.api.block import Block
from amulet.api.registry import BlockManager, BiomeManager
from .namespace import LevelNamespace


class MetadataNamespace(LevelNamespace, ABC):
    @abstractmethod
    def dimensions(self) -> Sequence[Dimension]:
        raise NotImplementedError

    @abstractmethod
    def bounds(self, dimension: Dimension) -> SelectionGroup:
        """The editable region of the dimension."""
        raise NotImplementedError

    @abstractmethod
    def default_block(self, dimension: Dimension) -> Block:
        """The default block for this dimension"""
        raise NotImplementedError

    @property
    @abstractmethod
    def block_palette(self) -> BlockManager:
        raise NotImplementedError

    @abstractmethod
    def default_biome(self, dimension: Dimension) -> BiomeType:
        """The default biome for this dimension"""
        raise NotImplementedError

    @property
    @abstractmethod
    def biome_palette(self) -> BiomeManager:
        raise NotImplementedError
