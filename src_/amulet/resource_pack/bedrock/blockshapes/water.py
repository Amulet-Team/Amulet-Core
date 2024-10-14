from amulet.block import Block
from amulet.mesh.block import BlockMesh, BlockMeshTransparency, get_unit_cube
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
                BlockMeshTransparency.FullTranslucent
                if transparency[0]
                else BlockMeshTransparency.FullOpaque
            ),
        )


BlockShape = Water()
