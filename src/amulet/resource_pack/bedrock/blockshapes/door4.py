from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.door import Door


class Door4(Door):
    @property
    def blockshape(self) -> str:
        return "door4"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 4


BlockShape = Door4()
