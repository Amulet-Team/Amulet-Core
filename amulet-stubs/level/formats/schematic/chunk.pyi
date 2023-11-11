from .data_types import BlockArrayType as BlockArrayType, BlockDataArrayType as BlockDataArrayType
from _typeshed import Incomplete
from amulet.selection import SelectionBox as SelectionBox
from amulet_nbt import CompoundTag as CompoundTag
from typing import List

class SchematicChunk:
    selection: Incomplete
    block_entities: Incomplete
    entities: Incomplete
    def __init__(self, selection: SelectionBox, blocks: BlockArrayType, data: BlockDataArrayType, block_entities: List[CompoundTag], entities: List[CompoundTag]) -> None: ...
    @property
    def blocks(self) -> BlockArrayType: ...
    _blocks: Incomplete
    @blocks.setter
    def blocks(self, blocks: BlockArrayType): ...
    @property
    def data(self) -> BlockDataArrayType: ...
    _data: Incomplete
    @data.setter
    def data(self, data: BlockDataArrayType): ...
