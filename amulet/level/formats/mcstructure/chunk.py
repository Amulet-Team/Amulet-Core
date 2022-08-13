from typing import List
import numpy

from amulet_nbt import CompoundTag

from amulet.api.selection import SelectionBox
from amulet.api.data_types import BlockCoordinates, AnyNDArray


class MCStructureChunk:
    __slots__ = (
        "selection",
        "blocks",
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
        assert isinstance(blocks, numpy.ndarray)
        assert (
            selection.shape == blocks.shape
        ), "blocks shape does not match the specified section shape"
        self.selection = selection
        self.blocks = blocks
        self.palette = palette
        self.block_entities = block_entities
        self.entities = entities

    def __eq__(self, other):
        return (
            isinstance(other, MCStructureChunk)
            and self.selection == other.selection
            and self.shape == other.shape
            and numpy.array_equal(self.blocks, other.blocks)
            and self.entities == other.entities
            and self.block_entities == other.block_entities
        )

    @property
    def location(self) -> BlockCoordinates:
        return self.selection.min
