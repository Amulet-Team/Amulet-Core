from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.cross_texture import (
    Cross,
)


class Cross0(Cross):
    @property
    def blockshape(self) -> str:
        return "cross_texture0"

    def texture_index(self, block: Block, aux_value: int) -> int:
        """The texture index to use within the list for the given Block"""
        return 0


BlockShape = Cross0()
