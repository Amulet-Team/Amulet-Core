from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.door import Door


class Door3(Door):
    @property
    def blockshape(self) -> str:
        return "door3"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 3


BlockShape = Door3()
