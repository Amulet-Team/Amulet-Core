from __future__ import annotations

from typing import List, TYPE_CHECKING

from amulet.api.selection import SelectionBox
from amulet.api.block import Block

if TYPE_CHECKING:
    from amulet.api.world import World


def replace(
    world: "World",
    selection_box: SelectionBox,
    original_blocks: List[Block],
    replacement_blocks: List[Block],
):
    if len(original_blocks) != len(replacement_blocks):
        raise Exception
    original_internal_ids = map(world.palette.get_add_block, original_blocks)
    replacement_internal_ids = map(world.palette.get_add_block, replacement_blocks)

    for subbox in selection_box.subboxes():
        block_generator = world.get_sub_chunks(*subbox.to_slice())
        for selection in block_generator:
            for original_id, replacement_id in zip(
                original_internal_ids, replacement_internal_ids
            ):
                blocks = selection.blocks.copy()
                blocks[blocks == original_id] = replacement_id
                selection.blocks = blocks
