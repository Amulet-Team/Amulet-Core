from __future__ import annotations

from typing import Iterable, Any
from abc import ABC, abstractmethod

from amulet.api.data_types import DimensionID, ChunkCoordinates, BiomeType
from amulet.block import Block
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup

RawChunkT = Any
NativeChunkT = Any
PlayerIDT = Any
RawPlayerT = Any


class RawDimension(ABC):
    __slots__ = ()

    @property
    @abstractmethod
    def dimension(self) -> DimensionID:
        raise NotImplementedError

    @abstractmethod
    def bounds(self) -> SelectionGroup:
        """The editable region of the dimension."""
        raise NotImplementedError

    @abstractmethod
    def default_block(self) -> Block:
        """The default block for this dimension"""
        raise NotImplementedError

    @abstractmethod
    def default_biome(self) -> BiomeType:
        """The default biome for this dimension"""
        raise NotImplementedError

    @abstractmethod
    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]:
        """Get an iterable of all the chunk coordinates that exist in the raw level data."""
        raise NotImplementedError

    @abstractmethod
    def has_chunk(self, cx: int, cz: int) -> bool:
        """Check if the chunk exists in the raw level data."""
        raise NotImplementedError

    @abstractmethod
    def delete_chunk(self, cx: int, cz: int):
        raise NotImplementedError

    @abstractmethod
    def get_raw_chunk(self, cx: int, cz: int) -> RawChunkT:
        """
        Get the chunk data in its raw format.
        This is usually the exact data that exists on disk.
        The raw chunk format varies between each level class.
        """
        raise NotImplementedError

    @abstractmethod
    def set_raw_chunk(self, cx: int, cz: int, chunk: RawChunkT):
        """Set the chunk in its raw format."""
        raise NotImplementedError

    @abstractmethod
    def get_native_chunk(self, cx: int, cz: int) -> NativeChunkT:
        """
        Get the raw chunk data loaded into an easier to use format.
        Block, biome and other array data should be loaded into editable arrays.
        """
        raise NotImplementedError

    @abstractmethod
    def set_native_chunk(self, cx: int, cz: int, chunk: NativeChunkT):
        """Set the chunk in its native format."""
        raise NotImplementedError

    @abstractmethod
    def get_universal_chunk(self, cx: int, cz: int) -> Chunk:
        """Get the chunk in the universal format."""

    @abstractmethod
    def set_universal_chunk(self, cx: int, cz: int, chunk: Chunk):
        """Set the chunk in the universal format."""
        raise NotImplementedError

    @abstractmethod
    def raw_to_native_chunk(self, chunk: RawChunkT) -> NativeChunkT:
        raise NotImplementedError

    @abstractmethod
    def native_to_raw_chunk(self, chunk: NativeChunkT) -> RawChunkT:
        raise NotImplementedError

    @abstractmethod
    def native_to_universal_chunk(self, chunk: NativeChunkT) -> Chunk:
        raise NotImplementedError

    @abstractmethod
    def universal_to_native_chunk(self, chunk: Chunk) -> NativeChunkT:
        raise NotImplementedError


class RawLevel(ABC):
    """
    A class with raw access to the level.
    All of these methods directly read from or write to the level.
    There is no way to undo changes made with these methods.
    """

    __slots__ = ()

    @abstractmethod
    def dimensions(self) -> frozenset[DimensionID]:
        raise NotImplementedError

    @abstractmethod
    def get_dimension(self, dimension: DimensionID) -> RawDimension:
        raise NotImplementedError

    @abstractmethod
    def players(self) -> Iterable[PlayerIDT]:
        raise NotImplementedError

    @abstractmethod
    def has_player(self, player_id: PlayerIDT) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_raw_player(self, player_id: PlayerIDT) -> RawPlayerT:
        raise NotImplementedError

    @abstractmethod
    def set_raw_player(self, player_id: PlayerIDT, player: RawPlayerT):
        raise NotImplementedError


class BufferedRawLevel(RawLevel):
    """
    A class with raw access to the level.
    All of these methods directly read from or write to the level.
    There is no way to undo changes made with these methods.

    This is a special case where the methods save to an in-memory buffer and :meth:`save` saves the data to the level.
    This is used for structure levels where the whole level must be read and written in one go.
    """

    __slots__ = ()

    @abstractmethod
    def save(self):
        raise NotImplementedError
