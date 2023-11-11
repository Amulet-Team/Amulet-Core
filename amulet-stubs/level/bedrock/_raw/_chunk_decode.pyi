import numpy
from ._dimension import BedrockRawDimension as BedrockRawDimension
from ._level import BedrockRawLevel as BedrockRawLevel
from _typeshed import Incomplete
from amulet.block import Block as Block
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.chunk.components.biome import Biome2DComponent as Biome2DComponent, Biome3DComponent as Biome3DComponent
from amulet.chunk.components.block import BlockComponent as BlockComponent
from amulet.chunk.components.block_entity import BlockEntityComponent as BlockEntityComponent
from amulet.chunk.components.entity import EntityComponent as EntityComponent
from amulet.chunk.components.height_2d import Height2DComponent as Height2DComponent
from amulet.entity import Entity as Entity
from amulet.level.bedrock._raw import BedrockRawChunk as BedrockRawChunk
from amulet.level.bedrock.chunk import BedrockChunk as BedrockChunk, BedrockChunk0 as BedrockChunk0, BedrockChunk29 as BedrockChunk29
from amulet.level.bedrock.chunk.components.finalised_state import FinalisedStateComponent as FinalisedStateComponent
from amulet.utils.world_utils import fast_unique as fast_unique, from_nibble_array as from_nibble_array
from amulet_nbt import ListTag as ListTag, NamedTag
from typing import Any, Dict, List, Optional, Tuple, TypeVar

log: Incomplete
SubChunkNDArray = numpy.ndarray
AnyNDArray = numpy.ndarray
T = TypeVar('T')

def cast(obj: Any, cls: type[T]) -> T: ...
def raw_to_native(level: BedrockRawLevel, dimension: BedrockRawDimension, raw_chunk: BedrockRawChunk) -> BedrockChunk: ...
def _load_subchunks(subchunks: dict[int, Optional[bytes]]) -> tuple[dict[int, SubChunkNDArray], AnyNDArray]:
    '''
    Load a list of bytes objects which contain chunk data
    This function should be able to load all sub-chunk formats (technically before it)
    All sub-chunks will almost certainly all have the same sub-chunk version but
    it should be able to handle a case where that is not true.

    As such this function will return a Chunk and a rather complicated block_palette
    The newer formats allow multiple blocks to occupy the same space and the
    newer versions also include a version ber block. So this will also need
    returning for the translator to handle.

    The block_palette will be a numpy array containing tuple objects
        The tuple represents the "block" however can contain more than one Block object.
        Inside the tuple are one or more tuples.
            These include the block version number and the block itself
                The block version number will be either None if no block version is given
                or a tuple containing 4 ints.

                The block will be either a Block class for the newer formats or a tuple of two ints for the older formats
    '''
def _load_palette_blocks(data: bytes) -> Tuple[numpy.ndarray, List[NamedTag], bytes]: ...
def _decode_3d_biomes(data: bytes, floor_cy: int) -> Dict[int, numpy.ndarray]: ...
def _decode_packed_array(data: bytes) -> Tuple[bytes, int, Optional[numpy.ndarray]]:
    """
    Parse a packed array as documented here
    https://gist.github.com/Tomcc/a96af509e275b1af483b25c543cfbf37

    :param data: The data to parse
    :return:
    """
def _unpack_nbt_list(raw_nbt: bytes) -> List[NamedTag]: ...
def _decode_block_entity_list(block_entities: List[NamedTag]) -> List[tuple[tuple[int, int, int], BlockEntity]]: ...
def _decode_block_entity(nbt: NamedTag) -> Optional[tuple[tuple[int, int, int], BlockEntity]]: ...
def _decode_entity_list(entities: List[NamedTag]) -> List[Entity]: ...
def _decode_entity(nbt: NamedTag) -> Optional[Entity]: ...
