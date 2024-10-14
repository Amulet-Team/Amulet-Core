from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.cube import Cube


class SlabDouble(Cube):
    @property
    def blockshape(self) -> str:
        return "slab_double"

    def texture_index(self, block: Block, aux_value: int) -> int:
        """The texture index to use within the list for the given Block"""
        return aux_value % 8


BlockShape = SlabDouble()
