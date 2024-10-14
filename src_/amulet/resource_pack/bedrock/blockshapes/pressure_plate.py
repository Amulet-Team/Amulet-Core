from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock,
)
import amulet_nbt


class PressurePlate(PartialBlock):
    def is_valid(self, block: Block) -> bool:
        return isinstance(block.properties.get("redstone_signal"), amulet_nbt.TAG_Int)

    @property
    def blockshape(self) -> str:
        return "pressure_plate"

    def bounds(
        self, block: Block
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
        if block.properties["redstone_signal"].py_data >= 1:
            return (1 / 16, 15 / 16), (0, 1 / 32), (1 / 16, 15 / 16)
        else:
            return (1 / 16, 15 / 16), (0, 1 / 16), (1 / 16, 15 / 16)

    @property
    def do_not_cull(self) -> tuple[bool, bool, bool, bool, bool, bool]:
        return False, True, True, True, True, True


BlockShape = PressurePlate()
