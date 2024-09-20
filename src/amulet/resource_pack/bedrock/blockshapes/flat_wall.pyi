from amulet.block import Block as Block
from amulet.mesh.block.block_mesh import BlockMesh as BlockMesh
from amulet.mesh.block.block_mesh import Transparency as Transparency
from amulet.resource_pack.bedrock.blockshapes.default import Default as Default

class FlatWall(Default):
    @property
    def tint(self) -> tuple[float, float, float]: ...
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
