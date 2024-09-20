import abc
from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, TypeVar

from amulet.biome import Biome as Biome
from amulet.block import BlockStack as BlockStack
from amulet.chunk import Chunk as Chunk
from amulet.data_types import ChunkCoordinates as ChunkCoordinates
from amulet.data_types import DimensionId as DimensionId
from amulet.selection import SelectionGroup as SelectionGroup

PlayerIDT = TypeVar("PlayerIDT")
RawPlayerT = TypeVar("RawPlayerT")
ChunkT = TypeVar("ChunkT", bound=Chunk)
RawChunkT = TypeVar("RawChunkT")

class RawDimension(ABC, Generic[RawChunkT, ChunkT], metaclass=abc.ABCMeta):
    @property
    @abstractmethod
    def dimension_id(self) -> DimensionId: ...
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
        """Get the chunk data in its raw format.

        This is usually the exact data that exists on disk.
        The raw chunk format varies between each level class.
        Each call to this method will return a unique object.

        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :return: The raw chunk.
        """

    @abstractmethod
    def set_raw_chunk(self, cx: int, cz: int, chunk: RawChunkT) -> None:
        """Set the chunk in its raw format."""

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

    @abstractmethod
    def native_chunk_to_raw_chunk(self, chunk: ChunkT, cx: int, cz: int) -> RawChunkT:
        """Pack the data from the editable classes into the raw format.

        This takes ownership of the chunk object.

        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :param chunk: The native chunk to pack
        :return: The packed chunk.
        """

RawDimensionT = TypeVar("RawDimensionT", bound=RawDimension)

class RawLevel(ABC, Generic[RawDimensionT], metaclass=abc.ABCMeta):
    """
    A class with raw access to the level.
    All of these methods directly read from or write to the level.
    There is no way to undo changes made with these methods.
    """

    @abstractmethod
    def dimension_ids(self) -> frozenset[DimensionId]: ...
    @abstractmethod
    def get_dimension(self, dimension_id: DimensionId) -> RawDimensionT: ...

RawLevelT = TypeVar("RawLevelT", bound=RawLevel)

class RawLevelFriend(Generic[RawLevelT]):
    """A base class for friends of the raw level that need to store a pointer to the raw level"""

    def __init__(self, raw_level_ref: Callable[[], RawLevelT | None]) -> None: ...

class RawLevelPlayerComponent(
    ABC, Generic[PlayerIDT, RawPlayerT], metaclass=abc.ABCMeta
):
    """An extension for the RawLevel class for implementations that have player data."""

    @abstractmethod
    def players(self) -> Iterable[PlayerIDT]: ...
    @abstractmethod
    def has_player(self, player_id: PlayerIDT) -> bool: ...
    @abstractmethod
    def get_raw_player(self, player_id: PlayerIDT) -> RawPlayerT: ...
    @abstractmethod
    def set_raw_player(self, player_id: PlayerIDT, player: RawPlayerT) -> None: ...

class RawLevelBufferedComponent(ABC, metaclass=abc.ABCMeta):
    """
    An extension for the RawLevel class for implementations that need a data buffer.

    This should be used for formats that cannot stream data and must read and write the data in one go.
    """

    @abstractmethod
    def pre_save(self) -> None:
        """A method to run before data is pushed to the raw level.
        This is useful to save the level.dat before pushing chunk data."""

    @abstractmethod
    def save(self) -> None:
        """A method to run after data is pushed to the raw level.
        This is useful for structure files to write the actual data to disk."""
