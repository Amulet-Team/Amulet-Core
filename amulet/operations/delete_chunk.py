from amulet.api.selection import SelectionGroup
from amulet.api.data_types import Dimension
from amulet.api.chunk import Chunk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel


def delete_chunk(
    world: "BaseLevel",
    dimension: Dimension,
    source_box: SelectionGroup,
    load_original: bool = True,
):
    chunks = [
        (cx, cz)
        for (cx, cz) in source_box.chunk_locations()
        if world.has_chunk(cx, cz, dimension)
    ]
    iter_count = len(chunks)
    for count, (cx, cz) in enumerate(chunks):
        world.delete_chunk(cx, cz, dimension)

        if not load_original:
            # this part is kind of hacky.
            # Work out a propery API to do this.
            key = dimension, cx, cz
            if key not in world.chunks._history_database:
                world.chunks._register_original_entry(key, Chunk(cx, cz))

        yield (count + 1) / iter_count
