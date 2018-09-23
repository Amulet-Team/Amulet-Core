from __future__ import annotations

from typing import Union

import numpy

from api.selection import SelectionBox
from api.operation import Operation


class Fill(Operation):
    def __init__(self, target_box: SelectionBox, fill_block: Union[str, int]):
        self.target_box = target_box

        self.fill_block = fill_block

    def run_operation(self, world):

        if isinstance(self.fill_block, str):
            self.fill_block = numpy.where(world.block_definitions == self.fill_block)[
                0
            ][0]

        for target in self.target_box.subboxes():
            block_generator = world.get_sub_chunks(*target.to_slice())
            for selection in block_generator:
                prime = selection.blocks
                selection.blocks = numpy.full(
                    selection.blocks.shape, self.fill_block, selection.blocks.dtype
                )
