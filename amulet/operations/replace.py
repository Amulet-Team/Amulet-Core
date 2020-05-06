from __future__ import annotations

from typing import List, TYPE_CHECKING

from amulet.api.selection import SelectionGroup
from amulet.api.block import Block
from amulet.api.data_types import Dimension
from amulet import log

if TYPE_CHECKING:
    from amulet.api.world import World


def replace(
    world: "World", dimension: Dimension, selection: SelectionGroup, options: dict
):
    original_blocks = options.get("original_blocks", None)
    if not isinstance(original_blocks, list) and all(
        isinstance(block, Block) for block in original_blocks
    ):
        log.error("Replace operation was not given a list of source Block objects")
        return

    replacement_blocks = options.get("replacement_blocks", None)
    if not isinstance(replacement_blocks, list) and all(
        isinstance(block, Block) for block in replacement_blocks
    ):
        log.error("Replace operation was not given a list of destination Block objects")
        return
    original_blocks: List[Block]
    replacement_blocks: List[Block]

    if len(original_blocks) != len(replacement_blocks):
        if len(replacement_blocks) == 1:
            replacement_blocks = replacement_blocks * len(original_blocks)
        else:
            log.error(
                "Replace operation must be given the same number of destination blocks as source blocks"
            )

    original_internal_ids = list(map(world.palette.get_add_block, original_blocks))
    replacement_internal_ids = list(
        map(world.palette.get_add_block, replacement_blocks)
    )

    for chunk, slices, _ in world.get_chunk_slices(selection, dimension):
        old_blocks = chunk.blocks[slices]
        new_blocks = old_blocks.copy()
        for original_id, replacement_id in zip(
            original_internal_ids, replacement_internal_ids
        ):
            new_blocks[old_blocks == original_id] = replacement_id
        chunk.blocks[slices] = new_blocks
        chunk.changed = True
