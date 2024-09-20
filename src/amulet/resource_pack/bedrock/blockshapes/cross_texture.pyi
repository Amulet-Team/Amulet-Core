from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.mesh.block.block_mesh import BlockMesh as BlockMesh
from amulet.mesh.block.block_mesh import Transparency as Transparency
from amulet.resource_pack.bedrock.blockshapes.base_blockshape import (
    BaseBlockShape as BaseBlockShape,
)

class Cross(BaseBlockShape):
    @property
    def blockshape(self) -> str: ...
    def is_valid(self, block: Block) -> bool:
        """Does the given block have the correct properties to use this blockshape"""

    def texture_index(self, block: Block, aux_value: int) -> int:
        """The texture index to use within the list for the given Block"""

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

BlockShape: Incomplete
