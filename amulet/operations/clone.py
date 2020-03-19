from amulet.api.selection import Selection
from amulet.api.structure import Structure
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.world import World


def clone(world: "World", source: Selection, target: dict):
    dst_location = (target.get("x", 0), target.get("y", 0), target.get("z", 0))
    structure = Structure.from_world(world, source, 0)
    for (
        src_chunk,
        src_slices,
        _,
        (dst_cx, dst_cz),
        dst_slices,
        _,
    ) in structure.get_moved_chunk_slices(dst_location):
        world.get_chunk(dst_cx, dst_cz).blocks2[dst_slices] = src_chunk.blocks[
            src_slices
        ]
