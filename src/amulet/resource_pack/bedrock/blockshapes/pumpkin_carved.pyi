from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.resource_pack.bedrock.blockshapes.pumpkin import Pumpkin as Pumpkin

class PumpkinCarved(Pumpkin):
    @property
    def blockshape(self) -> str: ...
    def texture_index(self, block: Block, aux_value: int) -> int: ...

BlockShape: Incomplete
