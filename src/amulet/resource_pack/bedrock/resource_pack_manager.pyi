from typing import Iterable, Literal, TypedDict

from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.mesh.block.block_mesh import BlockMesh as BlockMesh
from amulet.resource_pack import BaseResourcePackManager as BaseResourcePackManager
from amulet.resource_pack.bedrock import BedrockResourcePack as BedrockResourcePack
from amulet.utils import comment_json as comment_json

from .blockshapes import BlockShapeClasses as BlockShapeClasses

class NumericalProperty(TypedDict):
    name: str
    type: Literal["byte"] | Literal["int"]
    value: int

class StrProperty(TypedDict):
    name: str
    type: Literal["string"]
    value: str

class StateDict(TypedDict):
    name: str
    data: int
    states: list[NumericalProperty | StrProperty]

class BlockPaletteDict(TypedDict):
    blocks: list[StateDict]

BlockShapes: Incomplete
AuxValues: Incomplete

def get_aux_value(block: Block) -> int: ...

class BedrockResourcePackManager(BaseResourcePackManager):
    """A class to load and handle the data from the packs.
    Packs are given as a list with the later packs overwriting the earlier ones."""

    def __init__(
        self,
        resource_packs: BedrockResourcePack | Iterable[BedrockResourcePack],
        load: bool = True,
    ) -> None: ...
    @property
    def textures(self) -> tuple[str, ...]:
        """Returns a tuple of all the texture paths in the resource pack."""

    def get_texture_path(self, namespace: str | None, relative_path: str) -> str:
        """Get the absolute texture path from the namespace and relative path pair"""
