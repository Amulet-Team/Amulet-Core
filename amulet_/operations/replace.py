from __future__ import annotations

from typing import List, TYPE_CHECKING
import logging

from amulet.selection import SelectionGroup
from amulet.block import Block
from amulet.data_types import DimensionId

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel

log = logging.getLogger(__name__)


def replace(
    world: "BaseLevel", dimension: DimensionId, selection: SelectionGroup, options: dict
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

    original_internal_ids = list(
        map(world.block_palette.block_to_index, original_blocks)
    )
    replacement_internal_ids = list(
        map(world.block_palette.block_to_index, replacement_blocks)
    )

    for chunk, slices, _ in world.get_chunk_slice_box(dimension, selection):
        old_blocks = chunk.blocks[slices]
        new_blocks = old_blocks.copy()
        for original_id, replacement_id in zip(
            original_internal_ids, replacement_internal_ids
        ):
            new_blocks[old_blocks == original_id] = replacement_id
        chunk.blocks[slices] = new_blocks
        chunk.changed = True