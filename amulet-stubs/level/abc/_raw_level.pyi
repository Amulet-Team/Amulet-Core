import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amulet.api.data_types import ChunkCoordinates as ChunkCoordinates, DimensionID as DimensionID
from amulet.biome import Biome as Biome
from amulet.block import BlockStack as BlockStack
from amulet.chunk import Chunk as Chunk
from amulet.selection import SelectionGroup as SelectionGroup
from typing import Generic, Iterable, TypeVar

PlayerIDT = TypeVar('PlayerIDT')
RawPlayerT = TypeVar('RawPlayerT')
RawDimensionT = TypeVar('RawDimensionT', bound='RawDimension')
RawLevelT = TypeVar('RawLevelT', bound='RawLevel')
ChunkT = TypeVar('ChunkT', bound=Chunk)
RawChunkT = TypeVar('RawChunkT')

class RawDimension(ABC, Generic[RawChunkT, ChunkT], metaclass=abc.ABCMeta):
    __slots__: Incomplete
    @property
    @abstractmethod
    def dimension(self) -> DimensionID: ...
    @abstractmethod
    def bounds(self) -> SelectionGroup:
        """The editable region of the dimension."""
    @abstractmethod
    def default_block(self) -> BlockStack:
        """The default block for this dimension"""
    @abstractmethod
    def default_biome(self) -> Biome:
        """The default biome for this dimension"""
    @abstractmethod
    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]:
        """Get an iterable of all the chunk coordinates that exist in the raw level data."""
    @abstractmethod
    def has_chunk(self, cx: int, cz: int) -> bool:
        """Check if the chunk exists in the raw level data."""
    @abstractmethod
    def delete_chunk(self, cx: int, cz: int) -> None: ...
    @abstractmethod
    def get_raw_chunk(self, cx: int, cz: int) -> RawChunkT:
        """
        Get the chunk data in its raw format.
        This is usually the exact data that exists on disk.
        The raw chunk format varies between each level class.
        """
    @abstractmethod
    def set_raw_chunk(self, cx: int, cz: int, chunk: RawChunkT) -> None:
        """Set the chunk in its raw format."""
    @abstractmethod
    def raw_chunk_to_native_chunk(self, cx: int, cz: int, raw_chunk: RawChunkT) -> ChunkT: ...
    @abstractmethod
    def native_chunk_to_raw_chunk(self, cx: int, cz: int, raw_chunk: ChunkT) -> RawChunkT: ...

class RawLevel(ABC, Generic[RawDimensionT], metaclass=abc.ABCMeta):
    """
    A class with raw access to the level.
    All of these methods directly read from or write to the level.
    There is no way to undo changes made with these methods.
    """
    __slots__: Incomplete
    @abstractmethod
    def dimensions(self) -> frozenset[DimensionID]: ...
    @abstractmethod
    def get_dimension(self, dimension: DimensionID) -> RawDimensionT: ...

class RawLevelPlayerComponent(ABC, Generic[PlayerIDT, RawPlayerT], metaclass=abc.ABCMeta):
    """An extension for the RawLevel class for implementations that have player data."""
    @abstractmethod
    def players(self) -> Iterable[PlayerIDT]: ...
    @abstractmethod
    def has_player(self, player_id: PlayerIDT) -> bool: ...
    @abstractmethod
    def get_raw_player(self, player_id: PlayerIDT) -> RawPlayerT: ...
    @abstractmethod
    def set_raw_player(self, player_id: PlayerIDT, player: RawPlayerT) -> None: ...

class RawLevelBufferedComponent(RawLevel, metaclass=abc.ABCMeta):
    """
    An extension for the RawLevel class for implementations that need a data buffer.

    This should be used for formats that cannot stream data and must read and write the data in one go.
    """
    __slots__: Incomplete
    @abstractmethod
    def save(self) -> None: ...
