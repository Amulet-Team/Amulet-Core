from __future__ import annotations

import numpy

from api.selection import SelectionBox
from api.operation import Operation
from api.blocks import Block


class Fill(Operation):
    def __init__(self, target_box: SelectionBox, fill_block: Block):
        self.target_box = target_box

        self.fill_block = fill_block

    def run_operation(self, world):
        internal_id = world.block_definitions[self.fill_block]

        for target in self.target_box.subboxes():
            block_generator = world.get_sub_chunks(*target.to_slice())
            for selection in block_generator:
                selection.blocks = numpy.full(
                    selection.blocks.shape, internal_id, selection.blocks.dtype
                )
