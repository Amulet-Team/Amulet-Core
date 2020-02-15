from __future__ import annotations

import numpy
from typing import TYPE_CHECKING

from amulet.api.selection import SelectionBox
from amulet.api.operation import Operation, register
from amulet.api.block import Block

if TYPE_CHECKING:
    from amulet.api.world import World


@register("fill")
class Fill(Operation):
    def __init__(self, target_box: SelectionBox, fill_block: Block):
        self.target_box = target_box

        self.fill_block = fill_block

    def run_operation(self, world: "World"):
        internal_id = world.palette.get_add_block(self.fill_block)

        for target in self.target_box.subboxes():
            block_generator = world.get_sub_chunks(*target.to_slice())
            for selection in block_generator:
                selection.blocks = numpy.full(
                    selection.blocks.shape, internal_id, selection.blocks.dtype
                )
