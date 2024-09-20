from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.mesh.block import BlockMesh as BlockMesh
from amulet.resource_pack.bedrock.blockshapes.cross_texture import Cross as Cross

class BubbleColumn(Cross):
    @property
    def blockshape(self) -> str: ...
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
