from __future__ import annotations

from typing import TYPE_CHECKING

from amulet.api.selection import SelectionGroup
from amulet.api.block import Block
from amulet.api.data_types import Dimension, OperationReturnType

if TYPE_CHECKING:
    from amulet.api.world import World


def fill(
    world: "World", dimension: Dimension, target_box: SelectionGroup, fill_block: Block
) -> OperationReturnType:
    if not isinstance(fill_block, Block):
        raise Exception("Fill operation was not given a Block object")
    internal_id = world.palette.get_add_block(fill_block)

    iter_count = len(list(world.get_chunk_slices(target_box, dimension, True)))
    count = 0

    for chunk, slices, _ in world.get_chunk_slices(target_box, dimension, True):
        chunk.blocks[slices] = internal_id
        chunk.changed = True
        count += 1
        yield count / iter_count
