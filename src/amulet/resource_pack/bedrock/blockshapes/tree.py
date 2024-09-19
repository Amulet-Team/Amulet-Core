from amulet.block import Block
from amulet.mesh.block import BlockMesh
from amulet.resource_pack.bedrock.blockshapes.cube import Cube
import amulet_nbt


class Tree(Cube):
    def is_valid(self, block: Block) -> bool:
        return isinstance(block.properties.get("pillar_axis"), amulet_nbt.TAG_String)

    @property
    def blockshape(self) -> str:
        return "tree"

    def texture_index(self, block: Block, aux_value: int) -> int:
        return aux_value % 4

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
        axis: str = block.properties["pillar_axis"].py_data

        model = super().get_block_model(
            block, down, up, north, east, south, west, transparency
        )
        if axis == "x":
            return model.rotate(1, 1)
        elif axis == "z":
            return model.rotate(1, 2)
        return model


BlockShape = Tree()
