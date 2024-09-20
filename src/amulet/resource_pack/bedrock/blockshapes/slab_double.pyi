from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.resource_pack.bedrock.blockshapes.cube import Cube as Cube

class SlabDouble(Cube):
    @property
    def blockshape(self) -> str: ...
    def texture_index(self, block: Block, aux_value: int) -> int:
        """The texture index to use within the list for the given Block"""

BlockShape: Incomplete
