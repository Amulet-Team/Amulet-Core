from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.door import Door


class Door2(Door):
    @property
    def blockshape(self) -> str:
        return "door2"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 2


BlockShape = Door2()
