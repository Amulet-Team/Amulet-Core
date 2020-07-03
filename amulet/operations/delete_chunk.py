from amulet.api.selection import SelectionGroup
from amulet.api.data_types import Dimension
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.world import World


def delete_chunk(world: "World", dimension: Dimension, source_box: SelectionGroup):
    iter_count = len(list(world.get_chunk_boxes(source_box, dimension)))
    count = 0

    for chunk, _ in world.get_chunk_boxes(source_box, dimension):
        cx, cz = chunk.coordinates
        world.delete_chunk(cx, cz, dimension)
        count += 1
        yield count / iter_count
