from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.mesh.block import BlockMesh as BlockMesh
from amulet.resource_pack.bedrock.blockshapes.cross_texture import Cross as Cross

class DoublePlant(Cross):
    def is_valid(self, block: Block) -> bool: ...
    @property
    def blockshape(self) -> str: ...
    def texture_index(self, block: Block, aux_value: int) -> int: ...
    def get_block_model(
        self,
        block: Block,
        down: str,
        up: str,
        north: str,
        east: str,
        south: str,
        west: str,
        transparency: tuple[bool, bool, bool, bool, bool, bool],
    ) -> BlockMesh: ...

BlockShape: Incomplete
