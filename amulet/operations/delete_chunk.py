from amulet.api.selection import Selection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.world import World


def delete_chunk(world: "World", source_box: Selection):
    for chunk, _ in world.get_chunk_slices(source_box):
        world.delete_chunk(*chunk.coordinates)
