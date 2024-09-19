from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.flat_wall import (
    FlatWall,
)
from amulet.mesh.block import BlockMesh
import amulet_nbt


class Vine(FlatWall):
    def is_valid(self, block: Block) -> bool:
        return isinstance(
            block.properties.get("vine_direction_bits"), amulet_nbt.TAG_Int
        )

    @property
    def blockshape(self) -> str:
        return "vine"

    @property
    def tint(self) -> tuple[float, float, float]:
        return 0, 1, 0

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
        models = []
        data: int = block.properties["vine_direction_bits"].py_data
        if data:
            model = super().get_block_model(
                block, down, up, north, east, south, west, transparency
            )
            if data & 1:
                models.append(model.rotate(0, 2))
            if data & 2:
                models.append(model.rotate(0, 3))
            if data & 4:
                models.append(model.rotate(0, 0))
            if data & 8:
                models.append(model.rotate(0, 1))
        return BlockMesh.merge(models)


BlockShape = Vine()
