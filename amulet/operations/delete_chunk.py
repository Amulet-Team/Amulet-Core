from amulet.api.selection import SelectionGroup
from amulet.api.data_types import Dimension
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.world import BaseLevel


def delete_chunk(world: "BaseLevel", dimension: Dimension, source_box: SelectionGroup):
    iter_count = len(list(world.get_chunk_boxes(dimension, source_box)))
    count = 0

    for chunk, _ in world.get_chunk_boxes(dimension, source_box):
        cx, cz = chunk.coordinates
        world.delete_chunk(cx, cz, dimension)
        count += 1
        yield count / iter_count
