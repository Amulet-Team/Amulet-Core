from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.mesh.block import BlockMesh as BlockMesh
from amulet.resource_pack.bedrock.blockshapes.cube import Cube as Cube

class Furnace(Cube):
    def is_valid(self, block: Block) -> bool: ...
    @property
    def blockshape(self) -> str: ...
    def texture_index(self, block: Block, aux_value: int) -> int: ...
    @property
    def rotation_map(self) -> dict[int, int]: ...
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
    ) -> BlockMesh: ...

BlockShape: Incomplete
