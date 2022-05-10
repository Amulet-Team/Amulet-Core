import sys
from typing import TYPE_CHECKING, Tuple, Generator, Optional
import numpy

from amulet.api.data_types import Dimension, BlockCoordinates, FloatTriplet
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.block import Block, UniversalAirBlock
from amulet.api.errors import ChunkDoesNotExist, ChunkLoadError
from amulet.api.chunk import Chunk
from amulet.api.registry import BlockManager
from amulet.utils.matrix import transform_matrix, displacement_matrix
import amulet.api.level

if TYPE_CHECKING:
    from .base_level import BaseLevel


def is_sub_block(skip_blocks: Tuple[Block, ...], b: Block) -> bool:
    """Is the Block `b` a sub-block of any block in skip_blocks."""
    for skip_block in skip_blocks:
        if skip_block.namespaced_name == b.namespaced_name:
            other_properties = b.properties
            if skip_block.properties == {
                key: other_properties[key] for key in skip_block.properties.keys()
            }:
                return True
    return False


def gen_paste_blocks(
    block_palette: BlockManager, skip_blocks: Tuple[Block, ...]
) -> numpy.ndarray:
    """Create a numpy bool array of all the blocks which should be pasted.

    :param block_palette: The block palette of the chunk.
    :param skip_blocks: Blocks to not copy. If a property is not defined it will match any value.
    :return: Bool array of which blocks to copy.
    """
    return numpy.invert(
        numpy.vectorize(lambda b: is_sub_block(skip_blocks, b))(block_palette.blocks)
    )


def clone(
    src_structure: "BaseLevel",
    src_dimension: Dimension,
    src_selection: SelectionGroup,
    dst_structure: "BaseLevel",
    dst_dimension: Dimension,
    dst_selection_bounds: SelectionGroup,
    location: BlockCoordinates,
    scale: FloatTriplet = (1.0, 1.0, 1.0),
    rotation: FloatTriplet = (0.0, 0.0, 0.0),
    include_blocks: bool = True,
    include_entities: bool = True,
    skip_blocks: Tuple[Block, ...] = (),
    copy_chunk_not_exist: bool = False,
) -> Generator[float, None, None]:
    """Clone the source object data into the destination object with an optional transform.
    The src and dst can be the same object.
    Note this command may change in the future. Refer to all keyword arguments via the keyword.
    :param src_structure: The source structure to paste into the destination structure.
    :param src_dimension: The dimension of the source structure to use.
    :param src_selection: The area of the source structure to copy.
    :param dst_structure: The destination structure to paste into.
    :param dst_dimension: The dimension of the destination structure to use.
    :param dst_selection_bounds: The area of the destination structure that can be modified.
    :param location: The location where the centre of the `src_structure` will be in the `dst_structure`
    :param scale: The scale in the x, y and z axis. These can be negative to mirror.
    :param rotation: The rotation in degrees around each of the axis.
    :param include_blocks: Include blocks from the `src_structure`.
    :param include_entities: Include entities from the `src_structure`.
    :param skip_blocks: If a block matches a block in this list it will not be copied.
    :param copy_chunk_not_exist: If a chunk does not exist in the source should it be copied over as air. Always False where `src_structure` is a World.
    :return: A generator of floats from 0 to 1 with the progress of the paste operation.
    """
    location = tuple(location)
    src_selection = src_selection.merge_boxes()
    if include_blocks or include_entities:
        # we actually have to do something
        if isinstance(src_structure, amulet.api.level.World):
            copy_chunk_not_exist = False

        # TODO: look into if this can be a float so it will always be the exact middle
        rotation_point: numpy.ndarray = (
            (src_selection.max_array + src_selection.min_array) // 2
        ).astype(int)

        if src_structure is dst_structure and src_dimension == dst_dimension:
            # copying from an object to itself in the same dimension.
            # if the selections do not overlap this can be achieved directly
            # if they do overlap the selection will first need extracting
            # TODO: implement the above
            if (
                tuple(rotation_point) == location
                and scale == (1.0, 1.0, 1.0)
                and rotation == (0.0, 0.0, 0.0)
            ):
                # The src_object was pasted into itself at the same location. Nothing will change so do nothing.
                return
            src_structure = src_structure.extract_structure(
                src_selection, src_dimension
            )
            src_dimension = src_structure.dimensions[0]

        src_structure: "BaseLevel"

        # TODO: I don't know if this is feasible for large boxes: get the intersection of the source and destination selections and iterate over that to minimise work
        if any(rotation) or any(s != 1 for s in scale):
            # if the selection needs transforming
            rotation_radians = tuple(numpy.radians(rotation))
            transform = numpy.matmul(
                transform_matrix(scale, rotation_radians, location),
                displacement_matrix(*-rotation_point),
            )

            last_src: Optional[Tuple[int, int]] = None
            src_chunk: Optional[
                Chunk
            ] = None  # None here means the chunk does not exist or failed to load. Treat it as if it was air.
            last_dst: Optional[Tuple[int, int]] = None
            dst_chunk: Optional[
                Chunk
            ] = None  # None here means the chunk failed to load. Do not modify it.

            sum_progress = 0
            volumes = tuple(
                box.sub_chunk_count() for box in src_selection.selection_boxes
            )
            sum_volumes = sum(volumes)
            volumes = tuple(vol / sum_volumes for vol in volumes)

            if include_blocks:
                blocks_to_skip = set(skip_blocks)
                for box_index, box in enumerate(src_selection.selection_boxes):
                    for progress, src_coords, dst_coords in box.transformed_points(
                        transform
                    ):
                        if src_coords is not None:
                            dst_cx, dst_cy, dst_cz = dst_coords[0] >> 4
                            if (dst_cx, dst_cz) != last_dst:
                                last_dst = dst_cx, dst_cz
                                try:
                                    dst_chunk = dst_structure.get_chunk(
                                        dst_cx, dst_cz, dst_dimension
                                    )
                                except ChunkDoesNotExist:
                                    dst_chunk = dst_structure.create_chunk(
                                        dst_cx, dst_cz, dst_dimension
                                    )
                                except ChunkLoadError:
                                    dst_chunk = None

                            src_coords = numpy.floor(src_coords).astype(int)
                            # due to how the coords are found dst_coords will all be in the same sub-chunk
                            src_chunk_coords = src_coords >> 4

                            # split the src coords into which sub-chunks they came from
                            unique_chunks, inverse, counts = numpy.unique(
                                src_chunk_coords,
                                return_inverse=True,
                                return_counts=True,
                                axis=0,
                            )
                            chunk_indexes = numpy.argsort(inverse)
                            src_block_locations = numpy.split(
                                src_coords[chunk_indexes], numpy.cumsum(counts)[:-1]
                            )
                            dst_block_locations = numpy.split(
                                dst_coords[chunk_indexes], numpy.cumsum(counts)[:-1]
                            )
                            for chunk_location, src_blocks, dst_blocks in zip(
                                unique_chunks, src_block_locations, dst_block_locations
                            ):
                                # for each src sub-chunk
                                src_cx, src_cy, src_cz = chunk_location
                                if (src_cx, src_cz) != last_src:
                                    last_src = src_cx, src_cz
                                    try:
                                        src_chunk = src_structure.get_chunk(
                                            src_cx, src_cz, src_dimension
                                        )
                                    except ChunkLoadError:
                                        src_chunk = None

                                if dst_chunk is not None:
                                    if (
                                        src_chunk is not None
                                        and src_cy in src_chunk.blocks
                                    ):
                                        # TODO implement support for individual block rotation
                                        block_ids = src_chunk.blocks.get_sub_chunk(
                                            src_cy
                                        )[tuple(src_blocks.T % 16)]

                                        for block_id in numpy.unique(block_ids):
                                            block = src_chunk.block_palette[block_id]
                                            if not is_sub_block(skip_blocks, block):
                                                mask = block_ids == block_id
                                                dst_blocks_ = dst_blocks[mask]

                                                transformed_block = src_structure.translation_manager.transform_universal_block(
                                                    block, transform
                                                )

                                                dst_chunk.blocks.get_sub_chunk(dst_cy)[
                                                    tuple(dst_blocks_.T % 16)
                                                ] = dst_chunk.block_palette.get_add_block(
                                                    transformed_block
                                                )

                                                src_blocks_ = src_blocks[mask]
                                                for src_location, dst_location in zip(
                                                    src_blocks_, dst_blocks_
                                                ):
                                                    src_location = tuple(
                                                        src_location.tolist()
                                                    )
                                                    dst_location = tuple(
                                                        dst_location.tolist()
                                                    )

                                                    if (
                                                        src_location
                                                        in src_chunk.block_entities
                                                    ):
                                                        dst_chunk.block_entities[
                                                            dst_location
                                                        ] = src_chunk.block_entities[
                                                            src_location
                                                        ].new_at_location(
                                                            *dst_location
                                                        )
                                                    elif (
                                                        dst_location
                                                        in dst_chunk.block_entities
                                                    ):
                                                        del dst_chunk.block_entities[
                                                            dst_location
                                                        ]

                                                dst_chunk.changed = True
                                    elif UniversalAirBlock not in blocks_to_skip:
                                        dst_chunk.blocks.get_sub_chunk(dst_cy)[
                                            tuple(dst_blocks.T % 16)
                                        ] = dst_chunk.block_palette.get_add_block(
                                            UniversalAirBlock
                                        )
                                        for location in dst_blocks:
                                            location = tuple(location.tolist())
                                            if location in dst_chunk.block_entities:
                                                del dst_chunk.block_entities[location]
                                        dst_chunk.changed = True
                        yield sum_progress + volumes[box_index] * progress
                    sum_progress += volumes[box_index]

        else:
            # the selection can be cloned as is
            # the transform from the structure location to the world location
            offset = numpy.asarray(location).astype(int) - rotation_point
            moved_min_location = src_selection.min_array + offset

            iter_count = len(
                list(
                    src_structure.get_moved_coord_slice_box(
                        src_dimension,
                        moved_min_location,
                        src_selection,
                        dst_structure.sub_chunk_size,
                        yield_missing_chunks=copy_chunk_not_exist,
                    )
                )
            )

            count = 0

            for (
                src_chunk,
                src_slices,
                src_box,
                (dst_cx, dst_cz),
                dst_slices,
                dst_box,
            ) in src_structure.get_moved_chunk_slice_box(
                src_dimension,
                moved_min_location,
                src_selection,
                dst_structure.sub_chunk_size,
                create_missing_chunks=copy_chunk_not_exist,
            ):
                src_chunk: Chunk
                src_slices: Tuple[slice, slice, slice]
                src_box: SelectionBox
                dst_cx: int
                dst_cz: int
                dst_slices: Tuple[slice, slice, slice]
                dst_box: SelectionBox

                # load the destination chunk
                try:
                    dst_chunk = dst_structure.get_chunk(dst_cx, dst_cz, dst_dimension)
                except ChunkDoesNotExist:
                    dst_chunk = dst_structure.create_chunk(
                        dst_cx, dst_cz, dst_dimension
                    )
                except ChunkLoadError:
                    count += 1
                    continue

                if include_blocks:
                    # a boolean array specifying if each index should be pasted.
                    paste_blocks = gen_paste_blocks(
                        src_chunk.block_palette, skip_blocks
                    )

                    # create a look up table converting the source block ids to the destination block ids
                    gab = numpy.vectorize(
                        dst_chunk.block_palette.get_add_block, otypes=[numpy.uint32]
                    )
                    lut = gab(src_chunk.block_palette.blocks)

                    # iterate through all block entities in the chunk and work out if the block is going to be overwritten
                    remove_block_entities = []
                    for block_entity_location in dst_chunk.block_entities.keys():
                        if block_entity_location in dst_box:
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

                    # copy over the source block entities if the source block is supposed to be pasted
                    for (
                        block_entity_location,
                        block_entity,
                    ) in src_chunk.block_entities.items():
                        if block_entity_location in src_box:
                            chunk_block_entity_location = numpy.array(
                                block_entity_location
                            )
                            chunk_block_entity_location[[0, 2]] %= 16
                            if paste_blocks[
                                src_chunk.blocks[tuple(chunk_block_entity_location)]
                            ]:
                                dst_chunk.block_entities.insert(
                                    block_entity.new_at_location(
                                        *offset + block_entity_location
                                    )
                                )

                    try:
                        block_mask = src_chunk.blocks[src_slices]
                        mask = paste_blocks[block_mask]
                        dst_chunk.blocks[dst_slices][mask] = lut[
                            src_chunk.blocks[src_slices]
                        ][mask]
                        dst_chunk.changed = True
                    except IndexError as e:
                        locals_copy = locals().copy()
                        import traceback

                        numpy_threshold = numpy.get_printoptions()["threshold"]
                        numpy.set_printoptions(threshold=sys.maxsize)
                        with open("clone_error.log", "w") as f:
                            for k, v in locals_copy.items():
                                f.write(f"{k}: {v}\n\n")
                        numpy.set_printoptions(threshold=numpy_threshold)
                        raise IndexError(
                            f"Error pasting.\nPlease notify the developers and include the clone_error.log file.\n{e}"
                        ) from e

                if include_entities:
                    # TODO: implement pasting entities when we support entities
                    pass

                count += 1
                yield count / iter_count

        yield 1.0
