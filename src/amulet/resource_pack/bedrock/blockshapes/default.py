from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.base_blockshape import (
    BaseBlockShape,
)


class Default(BaseBlockShape):
    def is_valid(self, block: Block) -> bool:
        """Does the given block have the correct properties to use this blockshape"""
        return True

    def texture_index(self, block: Block, aux_value: int) -> int:
        """The texture index to use within the list for the given Block"""
        return aux_value % 16
