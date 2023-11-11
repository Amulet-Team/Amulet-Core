import numpy
from _typeshed import Incomplete
from amulet.api.data_types import AnyNDArray as AnyNDArray, BlockCoordinates as BlockCoordinates
from amulet.selection import SelectionBox as SelectionBox
from amulet_nbt import CompoundTag as CompoundTag
from typing import List

class SpongeSchemChunk:
    __slots__: Incomplete
    selection: Incomplete
    palette: Incomplete
    block_entities: Incomplete
    entities: Incomplete
    def __init__(self, selection: SelectionBox, blocks: numpy.ndarray, palette: AnyNDArray, block_entities: List[CompoundTag], entities: List[CompoundTag]) -> None: ...
    def __eq__(self, other): ...
    @property
    def location(self) -> BlockCoordinates: ...
    @property
    def blocks(self) -> numpy.ndarray: ...
    _blocks: Incomplete
    @blocks.setter
    def blocks(self, blocks: numpy.ndarray): ...
