from __future__ import annotations

from typing import List

from amulet.api.selection import SelectionBox
from amulet.api.operation import Operation, register
from amulet.api.block import Block


@register("replace")
class Replace(Operation):
    def __init__(
        self,
        selection_box: SelectionBox,
        original_blocks: List[Block],
        replacement_blocks: List[Block],
    ):
        self.original_blocks = original_blocks
        self.replacement_blocks = replacement_blocks
        self.selection_box = selection_box

        if len(original_blocks) != len(replacement_blocks):
            raise Exception

    def run_operation(self, world):
        original_internal_ids = map(
            world.block_manager.get_add_block, self.original_blocks
        )
        replacement_internal_ids = map(
            world.block_manager.get_add_block, self.replacement_blocks
        )

        for subbox in self.selection_box.subboxes():
            block_generator = world.get_sub_chunks(*subbox.to_slice())
            for selection in block_generator:
                for original_id, replacement_id in zip(
                    original_internal_ids, replacement_internal_ids
                ):
                    blocks = selection.blocks.copy()
                    blocks[blocks == original_id] = replacement_id
                    selection.blocks = blocks
