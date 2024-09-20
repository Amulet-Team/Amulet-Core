from typing import Any

from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.mesh.block import BlockMesh as BlockMesh
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock as PartialBlock,
)

class Chest(PartialBlock):
    @property
    def blockshape(self) -> str: ...
    def bounds(
        self, block: Block
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]: ...
    def texture_index(self, block: Block, aux_value: int) -> int: ...
    @property
    def do_not_cull(self) -> tuple[bool, bool, bool, bool, bool, bool]: ...
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
        *args: Any,
        **kwargs: Any
    ) -> BlockMesh: ...

BlockShape: Incomplete
