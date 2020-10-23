from typing import TYPE_CHECKING, Tuple, Generator, Optional
import numpy

from amulet.api.data_types import Dimension, BlockCoordinates, FloatTriplet
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.block import Block, UniversalAirBlock
from amulet.api.errors import ChunkDoesNotExist, ChunkLoadError
from amulet.api.chunk import Chunk
from amulet.api.registry import BlockManager
from amulet.utils.matrix import transform_matrix, displacement_matrix
import amulet.api.world

if TYPE_CHECKING:
    from .chunk_world import ChunkWorld


def gen_paste_blocks(
    block_palette: BlockManager, skip_blocks: Tuple[Block, ...]
) -> numpy.ndarray:
    """Create a numpy array of all the blocks which should be pasted.

    :param block_palette: The block palette of the chunk.
    :param skip_blocks: Blocks to not copy if they match exactly.
    :return:
    """
    return numpy.vectorize(lambda b: b not in skip_blocks)(block_palette.blocks())


def clone(
    src_structure: "ChunkWorld",
    src_dimension: Dimension,
    src_selection: SelectionGroup,
    dst_structure: "ChunkWorld",
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
    if include_blocks or include_entities:
        # we actually have to do something
        if isinstance(src_structure, amulet.api.world.World):
            copy_chunk_not_exist = False

        # TODO: look into if this can be a float so it will always be the exact middle
        rotation_point: numpy.ndarray = (
            (src_selection.max + src_selection.min) // 2
        ).astype(int)

        if src_structure is dst_structure and src_dimension == dst_dimension:
            # copying from an object to itself in the same dimension.
            # if the selections do not overlap this can be achieved directly
            # if they do overlap the selection will first need extracting
            # TODO: implement the above
            if (
                rotation_point == location
                and scale == (1.0, 1.0, 1.0)
                and rotation == (0.0, 0.0, 0.0)
            ):
                # The src_object was pasted into itself at the same location. Nothing will change so do nothing.
                return
            src_structure = src_structure.extract_structure(
                src_selection, src_dimension
            )

        src_structure: "ChunkWorld"

        # TODO: I don't know if this is feasible for large boxes: get the intersection of the source and destination selections and iterate over that to minimise work
        if any(rotation) or any(s != 1 for s in scale):
            rotation_radians = tuple(numpy.radians(rotation))
            transform = numpy.matmul(
                transform_matrix(scale, rotation_radians, location, "xyz"),
                displacement_matrix(*-rotation_point),
            )
            inverse_transform = numpy.linalg.inv(transform)

            dst_selection = (
                src_selection.transform((1, 1, 1), (0, 0, 0), tuple(-rotation_point))
                .transform(scale, rotation_radians, location)
                .intersection(dst_selection_bounds)
            )

            volume = dst_selection.volume
            index = 0

            last_src_cx: Optional[int] = None
            last_src_cz: Optional[int] = None
            src_chunk: Optional[
                Chunk
            ] = None  # None here means the chunk does not exist or failed to load. Treat it as if it was air.
            last_dst_cx: Optional[int] = None
            last_dst_cz: Optional[int] = None
            dst_chunk: Optional[
                Chunk
            ] = None  # None here means the chunk failed to load. Do not modify it.

            # TODO: find a way to do this without doing it block by block
            if include_blocks:
                for box in dst_selection.selection_boxes:
                    dst_coords = list(box.blocks())
                    coords_array = numpy.ones((len(dst_coords), 4), dtype=numpy.float)
                    coords_array[:, :3] = dst_coords
                    coords_array[:, :3] += 0.5
                    src_coords = (
                        numpy.floor(numpy.matmul(inverse_transform, coords_array.T))
                        .astype(int)
                        .T[:, :3]
                    )
                    for (dst_x, dst_y, dst_z), (src_x, src_y, src_z) in zip(
                        dst_coords, src_coords
                    ):
                        src_cx, src_cz = (src_x >> 4, src_z >> 4)
                        if (src_cx, src_cz) != (last_src_cx, last_src_cz):
                            last_src_cx = src_cx
                            last_src_cz = src_cz
                            try:
                                src_chunk = src_structure.get_chunk(
                                    src_cx, src_cz, src_dimension
                                )
                            except ChunkLoadError:
                                src_chunk = None

                        dst_cx, dst_cz = (dst_x >> 4, dst_z >> 4)
                        if (dst_cx, dst_cz) != (last_dst_cx, last_dst_cz):
                            last_dst_cx = dst_cx
                            last_dst_cz = dst_cz
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

                        if dst_chunk is not None:
                            if (dst_x, dst_y, dst_z) in dst_chunk.block_entities:
                                del dst_chunk.block_entities[(dst_x, dst_y, dst_z)]
                            if src_chunk is None:
                                dst_chunk.blocks[
                                    dst_x % 16, dst_y, dst_z % 16
                                ] = dst_chunk.block_palette.get_add_block(
                                    UniversalAirBlock
                                )
                            else:
                                # TODO implement support for individual block rotation
                                dst_chunk.blocks[
                                    dst_x % 16, dst_y, dst_z % 16
                                ] = dst_chunk.block_palette.get_add_block(
                                    src_chunk.block_palette[
                                        src_chunk.blocks[src_x % 16, src_y, src_z % 16]
                                    ]
                                )
                                if (src_x, src_y, src_z) in src_chunk.block_entities:
                                    dst_chunk.block_entities[
                                        (dst_x, dst_y, dst_z)
                                    ] = src_chunk.block_entities[
                                        (src_x, src_y, src_z)
                                    ].new_at_location(
                                        dst_x, dst_y, dst_z
                                    )
                            dst_chunk.changed = True

                        yield index / volume
                        index += 1

        else:
            # the transform from the structure location to the world location
            offset = numpy.asarray(location).astype(int) - rotation_point
            moved_min_location = src_selection.min + offset

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
                        dst_chunk.block_palette, skip_blocks
                    )

                    # create a look up table converting the source block ids to the destination block ids
                    gab = numpy.vectorize(
                        dst_chunk.block_palette.get_add_block, otypes=[numpy.uint32]
                    )
                    lut = gab(src_chunk.block_palette.blocks())

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

                    mask = paste_blocks[src_chunk.blocks[src_slices]]
                    dst_chunk.blocks[dst_slices][mask] = lut[
                        src_chunk.blocks[src_slices]
                    ][mask]
                    dst_chunk.changed = True

                if include_entities:
                    # TODO: implement pasting entities when we support entities
                    pass

                count += 1
                yield count / iter_count

        yield 1.0
