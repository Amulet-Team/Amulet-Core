import numpy
from typing import List

from amulet_nbt import CompoundTag

from amulet.api.selection import SelectionBox
from .data_types import BlockDataArrayType, BlockArrayType


class SchematicChunk:
    def __init__(
        self,
        selection: SelectionBox,
        blocks: BlockArrayType,
        data: BlockDataArrayType,
        block_entities: List[CompoundTag],
        entities: List[CompoundTag],
    ):
        self.selection = selection
        assert isinstance(blocks, numpy.ndarray) and blocks.dtype == numpy.uint16
        assert isinstance(data, numpy.ndarray) and data.dtype == numpy.uint8
        self.blocks = blocks
        self.data = data
        self.block_entities = block_entities
        self.entities = entities
