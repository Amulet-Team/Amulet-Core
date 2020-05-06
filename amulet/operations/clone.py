from amulet.api.selection import SelectionGroup
from amulet.api.structure import Structure
from amulet.api.data_types import Dimension
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.world import World


def clone(world: "World", dimension: Dimension, source: SelectionGroup, target: dict):
    dst_location = (target.get("x", 0), target.get("y", 0), target.get("z", 0))
    structure = Structure.from_world(world, source, dimension)
    for (
        src_chunk,
        src_slices,
        _,
        (dst_cx, dst_cz),
        dst_slices,
        _,
    ) in structure.get_moved_chunk_slices(dst_location):
        dst_chunk = world.get_chunk(dst_cx, dst_cz, dimension)
        dst_chunk.blocks[dst_slices] = src_chunk.blocks[src_slices]
        dst_chunk.changed = True
