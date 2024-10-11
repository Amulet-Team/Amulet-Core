from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.pumpkin import Pumpkin


class PumpkinLit(Pumpkin):
    @property
    def blockshape(self) -> str:
        return "pumpkin_lit"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 1


BlockShape = PumpkinLit()
