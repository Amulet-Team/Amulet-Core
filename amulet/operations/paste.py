from __future__ import annotations

from typing import TYPE_CHECKING
import numpy

from amulet.api.structure import Structure
from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist
from amulet.api.chunk import Chunk

if TYPE_CHECKING:
    from amulet.api.world import World


def paste(world: "World", dimension: int, structure: Structure, dst: dict):
    dst_location = (dst.get('x', 0), dst.get('y', 0), dst.get('z', 0))
    gab = numpy.vectorize(world.palette.get_add_block)
    lut = gab(structure.palette.blocks())
    for src_chunk, src_slices, _, (dst_cx, dst_cz), dst_slices, _ in structure.get_moved_chunk_slices(dst_location):
        try:
            dst_chunk = world.get_chunk(dst_cx, dst_cz, dimension)
        except ChunkDoesNotExist:
            dst_chunk = Chunk(dst_cx, dst_cz)
            world.put_chunk(dst_chunk, dimension)
        except ChunkLoadError:
            continue

        dst_chunk.blocks[dst_slices] = lut[src_chunk.blocks[src_slices]]
        dst_chunk.changed = True
