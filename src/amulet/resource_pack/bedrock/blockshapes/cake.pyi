from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock as PartialBlock,
)

class Cake(PartialBlock):
    def is_valid(self, block: Block) -> bool: ...
    @property
    def blockshape(self) -> str: ...
    def bounds(
        self, block: Block
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]: ...
    def texture_index(self, block: Block, aux_value: int) -> int: ...
    @property
    def do_not_cull(self) -> tuple[bool, bool, bool, bool, bool, bool]: ...

BlockShape: Incomplete
