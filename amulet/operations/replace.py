from __future__ import annotations

from typing import List, TYPE_CHECKING

from amulet.api.selection import SelectionBox
from amulet.api.block import Block
from amulet import log

if TYPE_CHECKING:
    from amulet.api.world import World


def replace(
    world: "World",
    selection_box: SelectionBox,
    options: dict
):
    original_blocks = options.get('original_blocks', None)
    if not isinstance(original_blocks, list) and all(isinstance(block, Block) for block in original_blocks):
        log.error('Replace operation was not given a list of source Block objects')
        return

    replacement_blocks = options.get('replacement_blocks', None)
    if not isinstance(replacement_blocks, list) and all(isinstance(block, Block) for block in replacement_blocks):
        log.error('Replace operation was not given a list of destination Block objects')
        return
    original_blocks: List[Block]
    replacement_blocks: List[Block]

    if len(original_blocks) != len(replacement_blocks):
        if len(replacement_blocks) == 1:
            replacement_blocks = replacement_blocks * len(original_blocks)
        else:
            log.error('Replace operation must be given the same number of destination blocks as source blocks')

    original_internal_ids = map(world.palette.get_add_block, original_blocks)
    replacement_internal_ids = map(world.palette.get_add_block, replacement_blocks)

    for subbox in selection_box.subboxes():
        block_generator = world.get_sub_chunks(*subbox.to_slice())
        for selection in block_generator:
            for original_id, replacement_id in zip(
                original_internal_ids, replacement_internal_ids
            ):
                selection.blocks[selection.blocks == original_id] = replacement_id
