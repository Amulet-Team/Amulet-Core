from typing import Any
from amulet.block import Block
from amulet.mesh.block import BlockMesh
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock,
)
import amulet_nbt


class PistonArm(PartialBlock):
    def is_valid(self, block: Block) -> bool:
        return isinstance(block.properties.get("facing_direction"), amulet_nbt.TAG_Int)

    @property
    def blockshape(self) -> str:
        return "piston_arm"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return 0

    @property
    def rotation_map(self) -> dict[int, tuple[int, int]]:
        return {0: (2, 0), 1: (0, 0), 2: (1, 2), 3: (1, 0), 4: (1, 1), 5: (1, 3)}

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
        *args: Any,
        **kwargs: Any
    ) -> BlockMesh:
        rotation = self.rotation_map.get(
            block.properties["facing_direction"].py_data, (0, 0)
        )

        return BlockMesh.merge(
            [
                super().get_block_model(
                    block,
                    down,
                    up,
                    north,
                    north,
                    north,
                    north,
                    transparency,
                    bounds=((0, 1), (12 / 16, 1), (0, 1)),
                    do_not_cull=(True, False, True, True, True, True),
                ),
                super().get_block_model(
                    block,
                    west,
                    west,
                    west,
                    west,
                    west,
                    west,
                    (transparency[5],) * 6,
                    bounds=((6 / 16, 10 / 16), (0, 12 / 16), (6 / 16, 10 / 16)),
                    do_not_cull=(False, False, True, True, True, True),
                ),
            ]
        ).rotate(*rotation)


BlockShape = PistonArm()
