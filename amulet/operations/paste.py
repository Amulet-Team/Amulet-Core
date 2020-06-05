from __future__ import annotations

from typing import TYPE_CHECKING, Sequence
import numpy

from amulet.api.structure import Structure
from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist
from amulet.api.chunk import Chunk
from amulet.api.data_types import Dimension, BlockCoordinates

if TYPE_CHECKING:
    from amulet.api.world import World


def paste(
        world: "World",
        dimension: Dimension,
        structure: Structure,
        locations: Sequence[BlockCoordinates],
        copy_air=True
):
    for _ in paste_iter(world, dimension, structure, locations, copy_air):
        pass


def paste_iter(
        world: "World",
        dimension: Dimension,
        structure: Structure,
        locations: Sequence[BlockCoordinates],
        copy_air=True
):
    gab = numpy.vectorize(world.palette.get_add_block)
    lut = gab(structure.palette.blocks())
    non_air = None
    if not copy_air:
        non_air = numpy.array(
            [
                block.namespaced_name != "universal_minecraft:air"
                for block in structure.palette.blocks()
            ]
        )

    for location_index, dst_location in enumerate(locations):
        offset = -structure.selection.min + dst_location

        iter_count = len(list(structure.get_moved_chunk_slices(dst_location)))
        count = 0

        for (
            src_chunk,
            src_slices,
            src_box,
            (dst_cx, dst_cz),
            dst_slices,
            dst_box,
        ) in structure.get_moved_chunk_slices(dst_location):
            try:
                dst_chunk = world.get_chunk(dst_cx, dst_cz, dimension)
            except ChunkDoesNotExist:
                dst_chunk = Chunk(dst_cx, dst_cz)
                world.put_chunk(dst_chunk, dimension)
            except ChunkLoadError:
                continue
            remove_block_entities = []
            for block_entity_location in dst_chunk.block_entities.keys():
                if block_entity_location in dst_box:
                    if copy_air:
                        remove_block_entities.append(block_entity_location)
                    else:
                        chunk_block_entity_location = (
                            numpy.array(block_entity_location) - offset
                        )
                        chunk_block_entity_location[[0, 2]] %= 16
                        if non_air[src_chunk.blocks[tuple(chunk_block_entity_location)]]:
                            remove_block_entities.append(block_entity_location)
            for block_entity_location in remove_block_entities:
                del dst_chunk.block_entities[block_entity_location]
            for block_entity_location, block_entity in src_chunk.block_entities.items():
                if block_entity_location in src_box:
                    dst_chunk.block_entities.insert(
                        block_entity.new_at_location(*offset + block_entity_location)
                    )

            if not copy_air:
                dst_blocks_copy = dst_chunk.blocks[dst_slices]
                mask = non_air[src_chunk.blocks[src_slices]]
                dst_blocks_copy[mask] = lut[src_chunk.blocks[src_slices]][mask]
                dst_chunk.blocks[dst_slices] = dst_blocks_copy
            else:
                dst_chunk.blocks[dst_slices] = lut[src_chunk.blocks[src_slices]]
            dst_chunk.changed = True

            count += 1
            yield (count / iter_count) * (location_index/len(locations))
