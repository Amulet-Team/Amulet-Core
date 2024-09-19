from amulet.block import Block
from amulet.mesh.block.block_mesh import BlockMesh, Transparency
from amulet.mesh.block.cube import get_unit_cube
from amulet.resource_pack.bedrock.blockshapes.cube import Cube


class Water(Cube):
    @property
    def blockshape(self) -> str:
        return "water"

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
        return get_unit_cube(
            down,
            down,
            down,
            down,
            down,
            down,
            (
                Transparency.FullTranslucent
                if transparency[0]
                else Transparency.FullOpaque
            ),
        )


BlockShape = Water()
