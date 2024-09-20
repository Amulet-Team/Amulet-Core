from typing import Iterable

from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.mesh.block.block_mesh import FACE_KEYS as FACE_KEYS
from amulet.mesh.block.block_mesh import BlockMesh as BlockMesh
from amulet.mesh.block.block_mesh import Transparency as Transparency
from amulet.mesh.block.cube import cube_face_lut as cube_face_lut
from amulet.mesh.block.cube import tri_face as tri_face
from amulet.mesh.block.cube import uv_rotation_lut as uv_rotation_lut
from amulet.mesh.util import rotate_3d as rotate_3d
from amulet.resource_pack import BaseResourcePackManager as BaseResourcePackManager
from amulet.resource_pack.java import JavaResourcePack as JavaResourcePack

log: Incomplete
UselessImageGroups: Incomplete

class JavaResourcePackManager(BaseResourcePackManager[JavaResourcePack]):
    """A class to load and handle the data from the packs.
    Packs are given as a list with the later packs overwriting the earlier ones."""

    def __init__(
        self,
        resource_packs: JavaResourcePack | Iterable[JavaResourcePack],
        load: bool = True,
    ) -> None: ...
    @property
    def textures(self) -> tuple[str, ...]:
        """Returns a tuple of all the texture paths in the resource pack."""

    def get_texture_path(self, namespace: str | None, relative_path: str) -> str:
        """Get the absolute texture path from the namespace and relative path pair"""

    @staticmethod
    def parse_state_val(val: str | bool) -> list:
        """Convert the json block state format into a consistent format."""
