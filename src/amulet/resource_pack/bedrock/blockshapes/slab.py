from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock,
)
import amulet_nbt


class Slab(PartialBlock):
    def is_valid(self, block: Block) -> bool:
        return isinstance(block.properties.get("top_slot_bit"), amulet_nbt.TAG_Byte)

    @property
    def blockshape(self) -> str:
        return "slab"

    def texture_index(self, block: Block, aux_value: int) -> int:
        """The texture index to use within the list for the given Block"""
        return aux_value % 8

    def bounds(
        self, block: Block
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
        if block.properties["top_slot_bit"].py_data:
            return (0, 1), (1 / 2, 1), (0, 1)
        else:
            return (0, 1), (0, 1 / 2), (0, 1)

    @property
    def do_not_cull(self) -> tuple[bool, bool, bool, bool, bool, bool]:
        return False, True, False, False, False, False


BlockShape = Slab()
