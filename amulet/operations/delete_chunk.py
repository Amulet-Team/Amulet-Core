from amulet.api.selection import Selection
from amulet.api.data_types import Dimension
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.world import World


def delete_chunk(world: "World", dimension: Dimension, source_box: Selection):
    iter_count = len(list(world.get_chunk_boxes(source_box, dimension)))
    count = 0

    for chunk, _ in world.get_chunk_boxes(source_box, dimension):
        world.delete_chunk(*chunk.coordinates, dimension)
        count += 1
        yield 100 * count / iter_count
