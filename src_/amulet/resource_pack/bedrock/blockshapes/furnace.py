from amulet.block import Block
from amulet.mesh.block import BlockMesh
from amulet.resource_pack.bedrock.blockshapes.cube import Cube
import amulet_nbt


class Furnace(Cube):
    def is_valid(self, block: Block) -> bool:
        return isinstance(block.properties.get("facing_direction"), amulet_nbt.TAG_Int)

    @property
    def blockshape(self) -> str:
        return "furnace"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 0

    @property
    def rotation_map(self) -> dict[int, int]:
        return {2: 2, 3: 0, 4: 1, 5: 3}

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
        rotation = self.rotation_map.get(
            block.properties["facing_direction"].py_data, 0
        )

        return (
            super()
            .get_block_model(block, down, up, north, east, south, west, transparency)
            .rotate(0, rotation)
        )


BlockShape = Furnace()
