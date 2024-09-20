from amulet.resource_pack.abc import BaseResourcePackManager as BaseResourcePackManager

from .block_mesh import BlockMesh as BlockMesh
from .cube import get_unit_cube as get_unit_cube

def get_missing_block(resource_pack: BaseResourcePackManager) -> BlockMesh: ...
