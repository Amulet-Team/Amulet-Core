from __future__ import annotations

from typing import TYPE_CHECKING

from amulet.api.selection import Selection
from amulet.api.block import Block
from amulet import log

if TYPE_CHECKING:
    from amulet.api.world import World


def fill(world: "World", target_box: Selection, options: dict):
    fill_block = options.get("fill_block", None)
    if not isinstance(fill_block, Block):
        log.error("Fill operation was not given a Block object")
        return
    fill_block: Block
    internal_id = world.palette.get_add_block(fill_block)

    for chunk, slices in world.get_chunk_slices(target_box):
        chunk.blocks[slices] = internal_id
