from __future__ import annotations

from typing import Iterable, TypeVar, Generic
from abc import ABC, abstractmethod

from amulet.api.data_types import DimensionID, ChunkCoordinates
from amulet.chunk import Chunk
from amulet.block import BlockStack
from amulet.biome import Biome
from amulet.selection import SelectionGroup

PlayerIDT = TypeVar("PlayerIDT")
RawPlayerT = TypeVar("RawPlayerT")
RawDimensionT = TypeVar("RawDimensionT", bound="RawDimension")
RawLevelT = TypeVar("RawLevelT", bound="RawLevel")
ChunkT = TypeVar("ChunkT", bound=Chunk)
RawChunkT = TypeVar("RawChunkT")


class RawDimension(ABC, Generic[RawChunkT, ChunkT]):
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
    def default_block(self) -> BlockStack:
        """The default block for this dimension"""
        raise NotImplementedError

    @abstractmethod
    def default_biome(self) -> Biome:
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
    def delete_chunk(self, cx: int, cz: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_raw_chunk(self, cx: int, cz: int) -> RawChunkT:
        """Get the chunk data in its raw format.

        This is usually the exact data that exists on disk.
        The raw chunk format varies between each level class.
        Each call to this method will return a unique object.

        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :return: The raw chunk.
        """
        raise NotImplementedError

    @abstractmethod
    def set_raw_chunk(self, cx: int, cz: int, chunk: RawChunkT) -> None:
        """Set the chunk in its raw format."""
        raise NotImplementedError

    @abstractmethod
    def raw_chunk_to_native_chunk(
        self, cx: int, cz: int, raw_chunk: RawChunkT
    ) -> ChunkT:
        """Unpack data from the raw chunk format (as stored on disk) into editable classes.

        This takes ownership of the raw_chunk object.

        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :param raw_chunk: The raw chunk to unpack.
        :return: The unpacked chunk.
        """
        raise NotImplementedError

    @abstractmethod
    def native_chunk_to_raw_chunk(self, cx: int, cz: int, chunk: ChunkT) -> RawChunkT:
        """Pack the data from the editable classes into the raw format.

        This takes ownership of the chunk object.

        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :param chunk: The native chunk to pack
        :return: The packed chunk.
        """
        raise NotImplementedError


class RawLevel(ABC, Generic[RawDimensionT]):
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
    def get_dimension(self, dimension: DimensionID) -> RawDimensionT:
        raise NotImplementedError


class RawLevelPlayerComponent(ABC, Generic[PlayerIDT, RawPlayerT]):
    """An extension for the RawLevel class for implementations that have player data."""

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
    def set_raw_player(self, player_id: PlayerIDT, player: RawPlayerT) -> None:
        raise NotImplementedError


class RawLevelBufferedComponent(RawLevel):
    """
    An extension for the RawLevel class for implementations that need a data buffer.

    This should be used for formats that cannot stream data and must read and write the data in one go.
    """

    __slots__ = ()

    @abstractmethod
    def save(self) -> None:
        raise NotImplementedError
