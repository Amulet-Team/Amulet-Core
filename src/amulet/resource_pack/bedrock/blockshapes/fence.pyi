from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock as PartialBlock,
)

class Fence(PartialBlock):
    @property
    def blockshape(self) -> str: ...
    def bounds(
        self, block: Block
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]: ...
    @property
    def do_not_cull(self) -> tuple[bool, bool, bool, bool, bool, bool]: ...

BlockShape: Incomplete
