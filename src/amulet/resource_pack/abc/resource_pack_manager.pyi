from typing import Generic, Iterator, TypeVar

from amulet.block import Block as Block
from amulet.block import BlockStack as BlockStack
from amulet.img import missing_no_icon_path as missing_no_icon_path
from amulet.mesh.block import BlockMesh as BlockMesh
from amulet.mesh.block.missing_block import get_missing_block as get_missing_block
from amulet.resource_pack.abc.resource_pack import BaseResourcePack as BaseResourcePack

PackT = TypeVar("PackT", bound=BaseResourcePack)

class BaseResourcePackManager(Generic[PackT]):
    """The base class that all resource pack managers must inherit from. Defines the base api."""

    def __init__(self) -> None: ...
    @property
    def pack_paths(self) -> list[str]: ...
    def reload(self) -> Iterator[float]:
        """Unload and reload resources"""

    @property
    def missing_no(self) -> str:
        """The path to the missing_no image"""

    @property
    def missing_block(self) -> BlockMesh: ...
    @property
    def textures(self) -> tuple[str, ...]:
        """Returns a tuple of all the texture paths in the resource pack."""

    def get_texture_path(self, namespace: str | None, relative_path: str) -> str:
        """Get the absolute texture path from the namespace and relative path pair"""

    def get_block_model(self, block_stack: BlockStack) -> BlockMesh:
        """Get a model for a block state.
        The block should already be in the resource pack format"""
