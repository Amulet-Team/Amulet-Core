import numpy

from amulet.block import Block
from amulet.mesh.block.block_mesh import BlockMesh, Transparency
from amulet.resource_pack.bedrock.blockshapes.default import Default


class FlatWall(Default):
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
                        0.0,
                        0.0,
                        1 / 16,
                        1.0,
                        0.0,
                        1 / 16,
                        1.0,
                        1.0,
                        1 / 16,
                        0.0,
                        1.0,
                        1 / 16,
                    ],
                    dtype=numpy.float32,
                )
            },
            {
                None: numpy.array(
                    [0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0], numpy.float32
                )
            },
            {None: numpy.array(self.tint * 4, numpy.float32)},
            {None: numpy.array([0, 1, 2, 0, 2, 3], numpy.uint32)},
            {None: numpy.array([0, 0], numpy.uint32)},
            (up,),
            Transparency.Partial,
        )
