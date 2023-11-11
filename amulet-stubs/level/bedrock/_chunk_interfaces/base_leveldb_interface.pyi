import numpy
from .leveldb_chunk_versions import chunk_to_game_version as chunk_to_game_version
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk, StatusFormats as StatusFormats
from amulet.api.chunk.blocks import Blocks as Blocks
from amulet.api.chunk.entity_list import EntityList as EntityList
from amulet.api.data_types import AnyNDArray as AnyNDArray, PlatformType as PlatformType, SubChunkNDArray as SubChunkNDArray, VersionIdentifierTuple as VersionIdentifierTuple, VersionNumberTuple as VersionNumberTuple
from amulet.api.wrapper import EntityCoordType as EntityCoordType, EntityIDType as EntityIDType, Interface as Interface, Translator as Translator
from amulet.block import Block as Block
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.entity import Entity as Entity
from amulet.level import loader as loader
from amulet.level.formats.leveldb_world.chunk import ChunkData as ChunkData
from amulet.utils.numpy_helpers import brute_sort_objects as brute_sort_objects
from amulet.utils.world_utils import fast_unique as fast_unique, from_nibble_array as from_nibble_array
from amulet_nbt import NamedTag, ReadContext as ReadContext, load_many as load_many, utf8_escape_decoder as utf8_escape_decoder
from typing import Any, Dict, Iterable, List, Optional, Tuple

log: Incomplete
_scale_grid: Incomplete

class BaseLevelDBInterface(Interface):
    chunk_version: int
    _feature_options: Incomplete
    _features: Incomplete
    def __init__(self) -> None: ...
    def _set_feature(self, feature: str, option: Any): ...
    def is_valid(self, key: Tuple) -> bool: ...
    def get_translator(self, max_world_version: Tuple[PlatformType, VersionNumberTuple], data: ChunkData = ...) -> Tuple['Translator', VersionNumberTuple]:
        """
        Get the Translator class for the requested version.
        :param max_world_version: The game version the world was last opened in. Version number tuple or data version number.
        :param data: Optional data to get translator based on chunk version rather than world version
        :return: Tuple[Translator, version number for PyMCTranslate to use]
        """
    @staticmethod
    def _get_sub_chunk_storage_byte(cy: int, min_y: int) -> bytes: ...
    def decode(self, cx: int, cz: int, chunk_data: ChunkData, bounds: Tuple[int, int]) -> Tuple[Chunk, AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param chunk_data: Raw chunk data provided by the format.
        :param bounds: The minimum and maximum height of the chunk.
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
    def encode(self, chunk: Chunk, palette: AnyNDArray, max_world_version: VersionIdentifierTuple, bounds: Tuple[int, int]) -> Dict[bytes, Optional[bytes]]: ...
    def _encode_subchunks(self, blocks: Blocks, palette: AnyNDArray, bounds: Tuple[int, int], max_world_version: VersionIdentifierTuple) -> Dict[int, Optional[bytes]]: ...
    def _save_subchunks_1(self, blocks: Blocks, palette: AnyNDArray) -> Dict[int, Optional[bytes]]: ...
    def _encode_height(self, chunk) -> bytes: ...
    def _encode_height_3d_biomes(self, chunk: Chunk, floor_cy: int, ceil_cy: int) -> bytes: ...
    @staticmethod
    def _encode_packed_array(arr: numpy.ndarray, min_bit_size: int = ...) -> bytes: ...
    def _save_palette_subchunk(self, blocks: numpy.ndarray, palette: List[NamedTag]) -> bytes:
        """Save a single layer of blocks in the block_palette format"""
    @staticmethod
    def _pack_nbt_list(nbt_list: List[NamedTag]): ...
    def _encode_entity_list(self, entities: EntityList) -> List[NamedTag]: ...
    def _encode_block_entity_list(self, block_entities: Iterable['BlockEntity']) -> List[NamedTag]: ...
