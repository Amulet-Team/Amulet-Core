import numpy
from .base_level import BaseLevel as BaseLevel
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import BlockCoordinates as BlockCoordinates, Dimension as Dimension, FloatTriplet as FloatTriplet
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist, ChunkLoadError as ChunkLoadError
from amulet.block import Block as Block, UniversalAirBlock as UniversalAirBlock
from amulet.palette import BlockPalette as BlockPalette
from amulet.selection import SelectionBox as SelectionBox, SelectionGroup as SelectionGroup
from amulet.utils.matrix import displacement_matrix as displacement_matrix, transform_matrix as transform_matrix
from typing import Generator, Tuple

def is_sub_block(skip_blocks: Tuple[Block, ...], b: Block) -> bool:
    """Is the Block `b` a sub-block of any block in skip_blocks."""
def gen_paste_blocks(block_palette: BlockPalette, skip_blocks: Tuple[Block, ...]) -> numpy.ndarray:
    """Create a numpy bool array of all the blocks which should be pasted.

    :param block_palette: The block palette of the chunk.
    :param skip_blocks: Blocks to not copy. If a property is not defined it will match any value.
    :return: Bool array of which blocks to copy.
    """
def clone(src_structure: BaseLevel, src_dimension: Dimension, src_selection: SelectionGroup, dst_structure: BaseLevel, dst_dimension: Dimension, dst_selection_bounds: SelectionGroup, location: BlockCoordinates, scale: FloatTriplet = ..., rotation: FloatTriplet = ..., include_blocks: bool = ..., include_entities: bool = ..., skip_blocks: Tuple[Block, ...] = ..., copy_chunk_not_exist: bool = ...) -> Generator[float, None, None]:
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
