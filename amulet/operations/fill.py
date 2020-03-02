from __future__ import annotations

import numpy
from typing import TYPE_CHECKING

from amulet.api.selection import SelectionBox
from amulet.api.block import Block

if TYPE_CHECKING:
    from amulet.api.world import World


def fill(world: "World", target_box: SelectionBox, fill_block: Block):
    internal_id = world.palette.get_add_block(fill_block)

    for target in target_box.subboxes():
        block_generator = world.get_sub_chunks(*target.to_slice())
        for selection in block_generator:
            selection.blocks = numpy.full(
                selection.blocks.shape, internal_id, selection.blocks.dtype
            )
