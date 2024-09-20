from amulet.block import Block as Block
from amulet.mesh.block.block_mesh import BlockMesh as BlockMesh
from amulet.mesh.block.block_mesh import Transparency as Transparency
from amulet.mesh.block.cube import get_cube as get_cube
from amulet.resource_pack.bedrock.blockshapes.default import Default as Default

BoundsType = tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
DoNotCullType = tuple[bool, bool, bool, bool, bool, bool]

class PartialBlock(Default):
    def bounds(self, block: Block) -> BoundsType: ...
    @property
    def do_not_cull(self) -> DoNotCullType: ...
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
        modify_uv: bool = True,
        bounds: BoundsType | None = None,
        do_not_cull: DoNotCullType | None = None,
    ) -> BlockMesh: ...
