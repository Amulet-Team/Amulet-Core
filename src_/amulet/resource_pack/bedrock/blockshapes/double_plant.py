from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.cross_texture import (
    Cross,
)
from amulet.mesh.block import BlockMesh
import amulet_nbt


class DoublePlant(Cross):
    def is_valid(self, block: Block) -> bool:
        return isinstance(block.properties.get("upper_block_bit"), amulet_nbt.TAG_Byte)

    @property
    def blockshape(self) -> str:
        return "double_plant"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return aux_value % 8

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
        if block.properties["upper_block_bit"].py_data:
            return super().get_block_model(block, up, up, up, up, up, up, transparency)
        else:
            return super().get_block_model(
                block, down, down, down, down, down, down, transparency
            )
        # TODO: add the sunflower face and tint the required blocks


BlockShape = DoublePlant()
