from __future__ import annotations

from typing import List, Optional

from amulet.api.data_types import BlockCoordinates
from amulet import Block
from amulet.api.entity import Entity
from amulet.api.block_entity import BlockEntity

import numpy


class ConstructionSection:
    __slots__ = (
        "sx",
        "sy",
        "sz",
        "blocks",
        "palette",
        "shape",
        "entities",
        "block_entities",
    )

    def __init__(
        self,
        min_position: BlockCoordinates,
        shape: BlockCoordinates,
        blocks: Optional[numpy.ndarray],
        palette: List[Block],
        entities: List[Entity],
        block_entities: List[BlockEntity],
    ):
        self.sx, self.sy, self.sz = min_position
        self.shape = shape
        self.blocks = blocks
        if blocks is not None:
            assert isinstance(self.blocks, numpy.ndarray)
            assert (
                self.shape == self.blocks.shape
            ), "blocks shape does not match the specified section shape"
        self.palette = palette
        self.entities = entities
        self.block_entities = block_entities

    def __eq__(self, other):
        return (
            isinstance(other, ConstructionSection)
            and self.sx == other.sx
            and self.sy == other.sy
            and self.sz == other.sz
            and self.shape == other.shape
            and numpy.equal(self.blocks, other.blocks).all()
            and self.entities == other.entities
            and self.block_entities == other.block_entities
        )

    @property
    def location(self) -> BlockCoordinates:
        return self.sx, self.sy, self.sz
