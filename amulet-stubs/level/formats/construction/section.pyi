import numpy
from _typeshed import Incomplete
from amulet.api.data_types import BlockCoordinates as BlockCoordinates
from amulet.block import Block as Block
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.entity import Entity as Entity
from typing import List, Optional

class ConstructionSection:
    __slots__: Incomplete
    shape: Incomplete
    blocks: Incomplete
    palette: Incomplete
    entities: Incomplete
    block_entities: Incomplete
    def __init__(self, min_position: BlockCoordinates, shape: BlockCoordinates, blocks: Optional[numpy.ndarray], palette: List[Block], entities: List[Entity], block_entities: List[BlockEntity]) -> None: ...
    def __eq__(self, other): ...
    @property
    def location(self) -> BlockCoordinates: ...
