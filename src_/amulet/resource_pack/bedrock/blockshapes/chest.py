from typing import Any

from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock,
)
from amulet.mesh.block import BlockMesh


class Chest(PartialBlock):
    @property
    def blockshape(self) -> str:
        return "chest"

    def bounds(
        self, block: Block
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
        return (1 / 16, 15 / 16), (0, 14 / 16), (1 / 16, 15 / 16)

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 0

    @property
    def do_not_cull(self) -> tuple[bool, bool, bool, bool, bool, bool]:
        return False, True, True, True, True, True

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
        *args: Any,
        **kwargs: Any
    ) -> BlockMesh:
        rotation = {2: 2, 3: 0, 4: 1, 5: 3}.get(
            block.properties["facing_direction"].py_data, 0
        )

        return (
            super()
            .get_block_model(
                block, down, up, north, east, south, west, transparency, modify_uv=False
            )
            .rotate(0, rotation)
        )


BlockShape = Chest()
