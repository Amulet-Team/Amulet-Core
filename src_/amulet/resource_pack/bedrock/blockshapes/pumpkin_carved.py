from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.pumpkin import Pumpkin


class PumpkinCarved(Pumpkin):
    @property
    def blockshape(self) -> str:
        return "pumpkin_carved"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 0


BlockShape = PumpkinCarved()
