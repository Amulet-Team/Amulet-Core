from amulet.block import Block
from amulet.mesh.block.block_mesh import BlockMesh, Transparency
from amulet.resource_pack.bedrock.blockshapes.base_blockshape import (
    BaseBlockShape,
)


class Air(BaseBlockShape):
    @property
    def blockshape(self) -> str:
        return "air"

    def is_valid(self, block: Block) -> bool:
        """Does the given block have the correct properties to use this blockshape"""
        return True

    def texture_index(self, block: Block, aux_value: int) -> int:
        """The texture index to use within the list for the given Block"""
        return 0

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
    ) -> BlockMesh:
        return BlockMesh(3, {}, {}, {}, {}, {}, (), Transparency.Partial)


BlockShape = Air()
