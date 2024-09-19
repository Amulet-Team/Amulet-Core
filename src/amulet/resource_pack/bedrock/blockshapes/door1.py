from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.door import Door


class Door1(Door):
    @property
    def blockshape(self) -> str:
        return "door1"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 1


BlockShape = Door1()
