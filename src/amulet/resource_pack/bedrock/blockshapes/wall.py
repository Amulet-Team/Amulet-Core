from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock,
)


class Wall(PartialBlock):
    @property
    def blockshape(self) -> str:
        return "wall"

    def bounds(
        self, block: Block
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
        return (4 / 16, 12 / 16), (0, 1), (4 / 16, 12 / 16)

    @property
    def do_not_cull(self) -> tuple[bool, bool, bool, bool, bool, bool]:
        return False, False, True, True, True, True


BlockShape = Wall()
