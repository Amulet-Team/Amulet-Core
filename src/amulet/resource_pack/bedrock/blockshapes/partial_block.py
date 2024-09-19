from typing import Optional

from amulet.block import Block
from amulet.mesh.block.block_mesh import BlockMesh, Transparency
from amulet.mesh.block.cube import get_cube
from amulet.resource_pack.bedrock.blockshapes.default import Default

BoundsType = tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
DoNotCullType = tuple[bool, bool, bool, bool, bool, bool]


class PartialBlock(Default):
    def bounds(self, block: Block) -> BoundsType:
        return (0, 1), (0, 1), (0, 1)

    @property
    def do_not_cull(self) -> DoNotCullType:
        return False, False, False, False, False, False

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
        bounds: Optional[BoundsType] = None,
        do_not_cull: Optional[DoNotCullType] = None,
    ) -> BlockMesh:
        bounds = bounds or self.bounds(block)
        if modify_uv:
            uv = (
                (bounds[0][0], bounds[2][0], bounds[0][1], bounds[2][1]),
                (bounds[0][0], bounds[2][0], bounds[0][1], bounds[2][1]),
                (bounds[0][0], 1 - bounds[1][1], bounds[0][1], 1 - bounds[1][0]),
                (bounds[2][0], 1 - bounds[1][1], bounds[2][1], 1 - bounds[1][0]),
                (bounds[0][0], 1 - bounds[1][1], bounds[0][1], 1 - bounds[1][0]),
                (bounds[2][0], 1 - bounds[1][1], bounds[2][1], 1 - bounds[1][0]),
            )
        else:
            uv = ((0, 0, 1, 1),) * 6
        return get_cube(
            down,
            up,
            north,
            east,
            south,
            west,
            Transparency.Partial,
            bounds=bounds,
            texture_uv=uv,
            do_not_cull=do_not_cull or self.do_not_cull,
        )
