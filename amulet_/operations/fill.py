from __future__ import annotations

from typing import TYPE_CHECKING

from amulet.selection import SelectionGroup
from amulet.block import Block
from amulet.data_types import DimensionId
from amulet.api.data_types import OperationReturnType

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel


def fill(
    world: "BaseLevel",
    dimension: DimensionId,
    target_box: SelectionGroup,
    fill_block: Block,
) -> OperationReturnType:
    if not isinstance(fill_block, Block):
        raise Exception("Fill operation was not given a Block object")
    internal_id = world.block_palette.block_to_index(fill_block)

    iter_count = len(list(world.get_coord_box(dimension, target_box, True)))
    count = 0

    for chunk, slices, _ in world.get_chunk_slice_box(dimension, target_box, True):
        chunk.blocks[slices] = internal_id
        chunk.changed = True
        count += 1
        yield count / iter_count