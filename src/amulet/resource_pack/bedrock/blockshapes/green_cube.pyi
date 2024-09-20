from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.mesh.block.block_mesh import BlockMesh as BlockMesh
from amulet.mesh.block.block_mesh import Transparency as Transparency
from amulet.mesh.block.cube import get_unit_cube as get_unit_cube
from amulet.resource_pack.bedrock.blockshapes.cube import Cube as Cube

class GreenCube(Cube):
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
