from __future__ import annotations

from typing import TYPE_CHECKING
import numpy

from amulet.api.structure import Structure
from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist
from amulet.api.chunk import Chunk
from amulet.api.data_types import Dimension, BlockCoordinates, FloatTriplet
from amulet.utils.matrix import transform_matrix

if TYPE_CHECKING:
    from amulet.api.world import World


def paste(
    world: "World",
    dimension: Dimension,
    structure: Structure,
    location: BlockCoordinates,
    scale: FloatTriplet,
    rotation: FloatTriplet,
    copy_air=True,
    copy_water=True,
    copy_lava=True,
):
    for _ in paste_iter(
        world,
        dimension,
        structure,
        location,
        scale,
        rotation,
        copy_air,
        copy_water,
        copy_lava,
    ):
        pass


def paste_iter(
    world: "World",
    dimension: Dimension,
    structure: Structure,
    location: BlockCoordinates,
    scale: FloatTriplet,
    rotation: FloatTriplet,
    copy_air=True,
    copy_water=True,
    copy_lava=True,
):
    gab = numpy.vectorize(world.palette.get_add_block, otypes=[numpy.uint32])
    lut = gab(structure.palette.blocks())
    filtered_mode = not all([copy_air, copy_lava, copy_water])
    filtered_blocks = []
    if not copy_air:
        filtered_blocks.append("universal_minecraft:air")
    if not copy_water:
        filtered_blocks.append("universal_minecraft:water")
    if not copy_lava:
        filtered_blocks.append("universal_minecraft:lava")
    if filtered_mode:
        paste_blocks = numpy.array(
            [
                any(
                    sub_block.namespaced_name not in filtered_blocks
                    for sub_block in block.block_tuple
                )
                for block in structure.palette.blocks()
            ]
        )
    else:
        paste_blocks = None

    rotation_point = numpy.floor(
        (structure.selection.max + structure.selection.min) / 2
    ).astype(int)

    if any(rotation) or any(s != 1 for s in scale):
        yield 0, "Rotating!"
        transformed_structure = yield from structure.transform_iter(scale, rotation)
        rotation_point = (
            numpy.matmul(
                transform_matrix(
                    (0, 0, 0), scale, -numpy.radians(numpy.flip(rotation)), "zyx"
                ),
                numpy.array([*rotation_point, 1]),
            )
            .T[:3]
            .round()
            .astype(int)
        )
    else:
        transformed_structure = structure

    offset = location - rotation_point
    moved_min_location = transformed_structure.selection.min + offset

    iter_count = len(
        list(
            transformed_structure.get_moved_chunk_slices(
                moved_min_location, generate_non_exists=True
            )
        )
    )
    count = 0

    yield 0, "Pasting!"
    for (
        src_chunk,
        src_slices,
        src_box,
        (dst_cx, dst_cz),
        dst_slices,
        dst_box,
    ) in transformed_structure.get_moved_chunk_slices(
        moved_min_location, generate_non_exists=True
    ):
        print(src_chunk)
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
                    if paste_blocks[
                        src_chunk.blocks[tuple(chunk_block_entity_location)]
                    ]:
                        remove_block_entities.append(block_entity_location)
        for block_entity_location in remove_block_entities:
            del dst_chunk.block_entities[block_entity_location]
        for block_entity_location, block_entity in src_chunk.block_entities.items():
            if block_entity_location in src_box:
                dst_chunk.block_entities.insert(
                    block_entity.new_at_location(*offset + block_entity_location)
                )

        if not copy_air:
            mask = paste_blocks[src_chunk.blocks[src_slices]]
            dst_chunk.blocks[dst_slices][mask] = lut[src_chunk.blocks[src_slices]][mask]
        else:
            dst_chunk.blocks[dst_slices] = lut[src_chunk.blocks[src_slices]]
        dst_chunk.changed = True

        count += 1
        yield count / iter_count
