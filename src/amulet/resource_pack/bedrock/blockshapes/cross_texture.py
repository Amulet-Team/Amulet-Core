import numpy

from amulet.block import Block
from amulet.mesh.block.block_mesh import BlockMesh, Transparency
from amulet.resource_pack.bedrock.blockshapes.base_blockshape import (
    BaseBlockShape,
)


class Cross(BaseBlockShape):
    @property
    def blockshape(self) -> str:
        return "cross_texture"

    def is_valid(self, block: Block) -> bool:
        """Does the given block have the correct properties to use this blockshape"""
        return True

    def texture_index(self, block: Block, aux_value: int) -> int:
        """The texture index to use within the list for the given Block"""
        return aux_value % 16

    @property
    def tint(self) -> tuple[float, float, float]:
        return 1, 1, 1

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
        return BlockMesh(
            3,
            {
                None: numpy.array(
                    [
                        0.0625,
                        0.0,
                        0.0625,
                        0.9375,
                        0.0,
                        0.9375,
                        0.9375,
                        1.0,
                        0.9375,
                        0.0625,
                        1.0,
                        0.0625,
                        0.0625,
                        0.0,
                        0.9375,
                        0.9375,
                        0.0,
                        0.0625,
                        0.9375,
                        1.0,
                        0.0625,
                        0.0625,
                        1.0,
                        0.9375,
                        0.9375,
                        0.0,
                        0.0625,
                        0.0625,
                        0.0,
                        0.9375,
                        0.0625,
                        1.0,
                        0.9375,
                        0.9375,
                        1.0,
                        0.0625,
                        0.9375,
                        0.0,
                        0.9375,
                        0.0625,
                        0.0,
                        0.0625,
                        0.0625,
                        1.0,
                        0.0625,
                        0.9375,
                        1.0,
                        0.9375,
                    ],
                    dtype=numpy.float32,
                )
            },
            {
                None: numpy.array(
                    [
                        0.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    numpy.float32,
                )
            },
            {None: numpy.array(self.tint * 16, numpy.float32)},
            {
                None: numpy.array(
                    [
                        0,
                        1,
                        2,
                        0,
                        2,
                        3,
                        4,
                        5,
                        6,
                        4,
                        6,
                        7,
                        8,
                        9,
                        10,
                        8,
                        10,
                        11,
                        12,
                        13,
                        14,
                        12,
                        14,
                        15,
                    ],
                    numpy.uint32,
                )
            },
            {
                None: numpy.array(
                    [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                    ],
                    numpy.uint32,
                )
            },
            (up,),
            Transparency.Partial,
        )


BlockShape = Cross()
