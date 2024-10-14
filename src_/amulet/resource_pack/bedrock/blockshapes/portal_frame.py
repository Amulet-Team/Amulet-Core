from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock,
)


class PortalFrame(PartialBlock):
    @property
    def blockshape(self) -> str:
        return "portal_frame"

    def bounds(
        self, block: Block
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
        return (0, 1), (0, 13 / 16), (0, 1)

    @property
    def do_not_cull(self) -> tuple[bool, bool, bool, bool, bool, bool]:
        return False, True, False, False, False, False


BlockShape = PortalFrame()
