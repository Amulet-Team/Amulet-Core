from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.cube import Cube
from amulet.mesh.block import BlockMesh
import amulet_nbt


class Pumpkin(Cube):
    def is_valid(self, block: Block) -> bool:
        return isinstance(block.properties.get("direction"), amulet_nbt.TAG_Int)

    @property
    def blockshape(self) -> str:
        return "pumpkin"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 2

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
        return (
            super()
            .get_block_model(block, down, up, north, east, south, west, transparency)
            .rotate(0, block.properties["direction"].py_data)
        )


BlockShape = Pumpkin()
