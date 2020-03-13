from amulet.api.selection import Selection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.world import World


def clone(world: "World", source: Selection, target: Selection):
    if len(source) != len(target):
        raise Exception(
            "Source Box and Target Box must have the same amount of subboxes"
        )

    for source_box, target_box in zip(source.subboxes, target.subboxes):
        if source_box.shape != target_box.shape:
            raise Exception("The shape of the selections needs to be the same")

    # TODO: fix this. This logic only works if the boxes overlap chunks in the same way.
    for (source_chunk, source_slice, _), (target_chunk, target_slice, _) in zip(
        world.get_chunk_slices(source), world.get_chunk_slices(target)
    ):
        target_chunk.blocks[target_slice] = source_chunk.blocks[source_slice]
