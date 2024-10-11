from amulet.block import Block
from amulet.mesh.block import BlockMesh, BlockMeshTransparency, get_unit_cube
from amulet.resource_pack.bedrock.blockshapes.default import Default


class Cube(Default):
    @property
    def blockshape(self) -> str:
        return "cube"

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
            up,
            north,
            east,
            south,
            west,
            (
                BlockMeshTransparency.FullTranslucent
                if any(transparency)
                else BlockMeshTransparency.FullOpaque
            ),
        )


BlockShape = Cube()
