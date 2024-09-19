from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.flat_wall import (
    FlatWall,
)
from amulet.mesh.block import BlockMesh


class Ladder(FlatWall):
    @property
    def blockshape(self) -> str:
        return "ladder"

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
    ) -> BlockMesh:
        rotation = {2: 2, 3: 0, 4: 1, 5: 3}.get(
            block.properties["facing_direction"].py_data, 0
        )

        return (
            super()
            .get_block_model(block, down, up, north, east, south, west, transparency)
            .rotate(0, rotation)
        )


BlockShape = Ladder()
