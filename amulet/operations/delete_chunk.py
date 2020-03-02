from amulet.api.selection import SelectionBox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.world import World


def delete_chunk(world: "World", source_box: SelectionBox):
    already_deleted_chunks = set()
    for subbox in source_box.subboxes():
        sub_chunks = world.get_sub_chunks(*subbox.to_slice())
        for sub_chunk in sub_chunks:
            chunk_coords = sub_chunk.parent_coordinates
            if chunk_coords in already_deleted_chunks:
                continue
            world.get_chunk(*chunk_coords)
            world.delete_chunk(*chunk_coords)
            already_deleted_chunks.add(chunk_coords)
