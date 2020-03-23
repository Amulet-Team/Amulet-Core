from amulet.api.selection import Selection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.world import World


def delete_chunk(world: "World", dimension: int, source_box: Selection):
    for chunk, _ in world.get_chunk_boxes(source_box, dimension):
        world.delete_chunk(*chunk.coordinates)
