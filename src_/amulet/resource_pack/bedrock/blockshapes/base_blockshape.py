from amulet.block import Block
from amulet.mesh.block import BlockMesh


class BaseBlockShape:
    @property
    def blockshape(self) -> str:
        raise NotImplementedError

    def is_valid(self, block: Block) -> bool:
        """Does the given block have the correct properties to use this blockshape"""
        raise NotImplementedError

    def texture_index(self, block: Block, aux_value: int) -> int:
        """The texture index to use within the list for the given Block"""
        raise NotImplementedError

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
        raise NotImplementedError
