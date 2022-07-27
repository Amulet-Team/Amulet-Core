from typing import List
import numpy

from amulet_nbt import CompoundTag

from amulet.api.selection import SelectionBox
from amulet.api.data_types import BlockCoordinates, AnyNDArray


class SpongeSchemChunk:
    __slots__ = (
        "selection",
        "_blocks",
        "palette",
        "shape",
        "entities",
        "block_entities",
    )

    def __init__(
        self,
        selection: SelectionBox,
        blocks: numpy.ndarray,
        palette: AnyNDArray,
        block_entities: List[CompoundTag],
        entities: List[CompoundTag],
    ):
        self.selection = selection
        self.blocks = blocks
        self.palette = palette
        self.block_entities = block_entities
        self.entities = entities

    def __eq__(self, other):
        return (
            isinstance(other, SpongeSchemChunk)
            and self.selection == other.selection
            and self.shape == other.shape
            and numpy.array_equal(self.blocks, other.blocks)
            and self.entities == other.entities
            and self.block_entities == other.block_entities
        )

    @property
    def location(self) -> BlockCoordinates:
        return self.selection.min

    @property
    def blocks(self) -> numpy.ndarray:
        return self._blocks

    @blocks.setter
    def blocks(self, blocks: numpy.ndarray):
        if not (
            isinstance(blocks, numpy.ndarray)
            and blocks.shape == self.selection.shape
            and numpy.issubdtype(blocks.dtype, numpy.integer)
        ):
            raise TypeError(
                "SpongeSchemChunk.blocks must be a integer numpy array with shape that matches selection"
            )
        self._blocks = blocks
