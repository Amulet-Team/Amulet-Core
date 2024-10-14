from amulet.block import Block
from amulet.mesh.block import BlockMesh
from amulet.resource_pack.bedrock.blockshapes.cube import Cube
import amulet_nbt


class Door(Cube):
    def is_valid(self, block: Block) -> bool:
        return isinstance(block.properties.get("upper_block_bit"), amulet_nbt.TAG_Byte)

    @property
    def blockshape(self) -> str:
        return "door"

    def texture_index(self, block: Block, aux_value: int) -> int:
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
        if block.properties["upper_block_bit"].py_data:
            return super().get_block_model(
                block, north, north, north, north, north, north, transparency
            )
        return super().get_block_model(
            block, down, down, down, down, down, down, transparency
        )


BlockShape = Door()
