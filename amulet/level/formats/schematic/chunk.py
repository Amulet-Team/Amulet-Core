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
        self.blocks = blocks
        self.data = data
        self.block_entities = block_entities
        self.entities = entities

    @property
    def blocks(self) -> BlockArrayType:
        return self._blocks

    @blocks.setter
    def blocks(self, blocks: BlockArrayType):
        if not (
            isinstance(blocks, numpy.ndarray)
            and blocks.shape == self.selection.shape
            and blocks.dtype == numpy.uint16
        ):
            raise TypeError(
                "SchematicChunk.blocks must be a uint16 numpy array with shape that matches selection"
            )
        self._blocks = blocks

    @property
    def data(self) -> BlockDataArrayType:
        return self._data

    @data.setter
    def data(self, data: BlockDataArrayType):
        if not (
            isinstance(data, numpy.ndarray)
            and data.shape == self.selection.shape
            and data.dtype == numpy.uint8
        ):
            raise TypeError(
                "SchematicChunk.data must be a uint8 numpy array with shape that matches selection"
            )
        self._data = data
