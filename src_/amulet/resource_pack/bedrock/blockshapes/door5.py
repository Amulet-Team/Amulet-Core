from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.door import Door


class Door5(Door):
    @property
    def blockshape(self) -> str:
        return "door5"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 5


BlockShape = Door5()
