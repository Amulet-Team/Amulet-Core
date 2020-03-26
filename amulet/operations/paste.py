from __future__ import annotations

from typing import TYPE_CHECKING

from amulet.api.selection import Selection
from amulet.api.structure import Structure

if TYPE_CHECKING:
    from amulet.api.world import World


def paste(world: "World", dimension: int, source: Selection, structure: Structure, dst: dict):
    dst_location = (dst.get('x', 0), dst.get('y', 0), dst.get('z', 0))
    for src_chunk, src_slices, _, (dst_cx, dst_cz), dst_slices, _ in structure.get_moved_chunk_slices(dst_location):
        dst_chunk = world.get_chunk(dst_cx, dst_cz, dimension)
        dst_chunk.blocks[dst_slices] = src_chunk.blocks[src_slices]
        dst_chunk.changed = True
