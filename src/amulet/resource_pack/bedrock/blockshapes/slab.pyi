from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock as PartialBlock,
)

class Slab(PartialBlock):
    def is_valid(self, block: Block) -> bool: ...
    @property
    def blockshape(self) -> str: ...
    def texture_index(self, block: Block, aux_value: int) -> int:
        """The texture index to use within the list for the given Block"""

    def bounds(
        self, block: Block
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]: ...
    @property
    def do_not_cull(self) -> tuple[bool, bool, bool, bool, bool, bool]: ...

BlockShape: Incomplete
