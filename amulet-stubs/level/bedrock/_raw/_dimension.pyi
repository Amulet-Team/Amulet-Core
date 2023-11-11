from ..chunk import BedrockChunk as BedrockChunk
from ._chunk import BedrockRawChunk as BedrockRawChunk
from ._chunk_decode import raw_to_native as raw_to_native
from ._constant import THE_END as THE_END, THE_NETHER as THE_NETHER
from ._level import BedrockRawLevelPrivate as BedrockRawLevelPrivate
from ._level_friend import BedrockRawLevelFriend as BedrockRawLevelFriend
from ._typing import InternalDimension as InternalDimension
from _typeshed import Incomplete
from amulet.api.data_types import ChunkCoordinates as ChunkCoordinates, DimensionID as DimensionID
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist
from amulet.biome import Biome as Biome
from amulet.block import Block as Block, BlockStack as BlockStack
from amulet.level.abc import RawDimension as RawDimension
from amulet.selection import SelectionGroup as SelectionGroup
from typing import Iterable

log: Incomplete

class BedrockRawDimension(BedrockRawLevelFriend, RawDimension[BedrockRawChunk, BedrockChunk]):
    _internal_dimension: Incomplete
    _alias: Incomplete
    _bounds: Incomplete
    def __init__(self, raw_data: BedrockRawLevelPrivate, internal_dimension: InternalDimension, alias: DimensionID, bounds: SelectionGroup) -> None: ...
    @property
    def dimension(self) -> DimensionID: ...
    def bounds(self) -> SelectionGroup:
        """The editable region of the dimension."""
    def default_block(self) -> BlockStack:
        """The default block for this dimension"""
    def default_biome(self) -> Biome:
        """The default biome for this dimension"""
    @property
    def internal_dimension(self) -> InternalDimension: ...
    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]: ...
    def _chunk_prefix(self, cx: int, cz: int) -> bytes: ...
    def has_chunk(self, cx: int, cz: int) -> bool: ...
    def delete_chunk(self, cx: int, cz: int): ...
    def get_raw_chunk(self, cx: int, cz: int) -> BedrockRawChunk:
        """
        Get a dictionary of chunk key extension in bytes to the raw data in the key.
        chunk key extension are the character(s) after <cx><cz>[level] in the key
        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :return:
        :raises:
            ChunkDoesNotExist if the chunk does not exist
        """
    def set_raw_chunk(self, cx: int, cz: int, chunk: BedrockRawChunk):
        """
        Set the raw data for a chunk
        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :param chunk: The chunk data to set.
        :return:
        """
    def raw_chunk_to_native_chunk(self, cx: int, cz: int, raw_chunk: BedrockRawChunk) -> BedrockChunk: ...
    def native_chunk_to_raw_chunk(self, cx: int, cz: int, raw_chunk: BedrockChunk) -> BedrockRawChunk: ...
