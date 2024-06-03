from __future__ import annotations

from typing import Iterable, TypeVar, Generic, Callable
from abc import ABC, abstractmethod
from weakref import ref

from amulet.data_types import ChunkCoordinates, DimensionId
from amulet.chunk import Chunk
from amulet.block import BlockStack
from amulet.biome import Biome
from amulet.selection import SelectionGroup

PlayerIDT = TypeVar("PlayerIDT")
RawPlayerT = TypeVar("RawPlayerT")
ChunkT = TypeVar("ChunkT", bound=Chunk)
RawChunkT = TypeVar("RawChunkT")


class RawDimension(ABC, Generic[RawChunkT, ChunkT]):
    __slots__ = ()

    @property
    @abstractmethod
    def dimension_id(self) -> DimensionId:
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
        self, raw_chunk: RawChunkT, cx: int, cz: int
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
    def native_chunk_to_raw_chunk(self, chunk: ChunkT, cx: int, cz: int) -> RawChunkT:
        """Pack the data from the editable classes into the raw format.

        This takes ownership of the chunk object.

        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :param chunk: The native chunk to pack
        :return: The packed chunk.
        """
        raise NotImplementedError


RawDimensionT = TypeVar("RawDimensionT", bound=RawDimension)


class RawLevel(ABC, Generic[RawDimensionT]):
    """
    A class with raw access to the level.
    All of these methods directly read from or write to the level.
    There is no way to undo changes made with these methods.
    """

    __slots__ = ("__weakref__",)

    @abstractmethod
    def dimension_ids(self) -> frozenset[DimensionId]:
        raise NotImplementedError

    @abstractmethod
    def get_dimension(self, dimension_id: DimensionId) -> RawDimensionT:
        raise NotImplementedError


RawLevelT = TypeVar("RawLevelT", bound=RawLevel)


class RawLevelFriend(Generic[RawLevelT]):
    """A base class for friends of the raw level that need to store a pointer to the raw level"""

    _r_ref: Callable[[], RawLevelT | None]

    __slots__ = ("_r_ref",)

    def __init__(self, raw_level_ref: Callable[[], RawLevelT | None]) -> None:
        self._r_ref = raw_level_ref

    @property
    def _r(self) -> RawLevelT:
        r = self._r_ref()
        if r is None:
            raise RuntimeError("Cannot access raw level")
        return r


class RawLevelPlayerComponent(ABC, Generic[PlayerIDT, RawPlayerT]):
    """An extension for the RawLevel class for implementations that have player data."""

    __slots__ = ()

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


class RawLevelBufferedComponent(ABC):
    """
    An extension for the RawLevel class for implementations that need a data buffer.

    This should be used for formats that cannot stream data and must read and write the data in one go.
    """

    __slots__ = ()

    @abstractmethod
    def pre_save(self) -> None:
        """A method to run before data is pushed to the raw level.
        This is useful to save the level.dat before pushing chunk data."""
        raise NotImplementedError

    @abstractmethod
    def save(self) -> None:
        """A method to run after data is pushed to the raw level.
        This is useful for structure files to write the actual data to disk."""
        raise NotImplementedError
