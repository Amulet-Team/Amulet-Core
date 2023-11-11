from _typeshed import Incomplete
from amulet.api import level as api_level
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import Dimension as Dimension, DimensionCoordinates as DimensionCoordinates
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist, ChunkLoadError as ChunkLoadError
from amulet.api.history.base import RevisionManager as RevisionManager
from amulet.api.history.data_types import EntryKeyType as EntryKeyType, EntryType as EntryType
from amulet.api.history.history_manager import DatabaseHistoryManager as DatabaseHistoryManager
from amulet.api.history.revision_manager import DBRevisionManager as DBRevisionManager
from leveldb import LevelDB as LevelDB
from typing import Dict, Generator, Iterable, Optional, Set, Tuple

class ChunkDBEntry(DBRevisionManager):
    __slots__: Incomplete
    _world: Incomplete
    _history_db: Incomplete
    def __init__(self, world: api_level.BaseLevel, history_db: LevelDB, prefix: str, initial_state: EntryType) -> None: ...
    @property
    def world(self) -> api_level.BaseLevel: ...
    def _serialise(self, path: str, entry: Optional[Chunk]) -> Optional[str]: ...
    def _deserialise(self, path: Optional[str]) -> Optional[Chunk]: ...

class ChunkManager(DatabaseHistoryManager):
    """
    The ChunkManager class is a class that handles chunks within a world.

    It handles the temporary database of chunks in RAM that can be directly modified.

    It handles a serialised version of the chunks on disk to reduce RAM usage.

    It also contains a history manager to allow undoing and redoing of changes.
    """
    _temporary_database: Dict[DimensionCoordinates, EntryType]
    _history_database: Dict[DimensionCoordinates, RevisionManager]
    DoesNotExistError = ChunkDoesNotExist
    LoadError = ChunkLoadError
    _prefix: str
    _level: Incomplete
    _history_db: Incomplete
    def __init__(self, level: api_level.BaseLevel, history_db: LevelDB) -> None:
        """
        Construct a :class:`ChunkManager` instance.

        Should not be directly used by third party code.

        :param level: The world that this chunk manager is associated with
        """
    @property
    def level(self) -> api_level.BaseLevel:
        """The level that this chunk manager is associated with."""
    def changed_chunks(self) -> Generator[DimensionCoordinates, None, None]:
        """The location of every chunk that has been changed since the last save."""
    def unload(self, safe_area: Optional[Tuple[Dimension, int, int, int, int]] = ...):
        """
        Unload all chunks from the temporary database that are not in the safe area.

        :param safe_area: The area that should not be unloaded [dimension, min_chunk_x, min_chunk_z, max_chunk_x, max_chunk_z]. If None will unload all chunk data.
        """
    def __contains__(self, item: DimensionCoordinates) -> bool:
        '''
        Is the chunk specified present in the level.

        >>> ("minecraft:overworld", 0, 0) in level.chunks
        True

        :param item: A tuple of dimension, chunk x coordinate and chunk z coordinate.
        :return: True if the chunk is present, False otherwise
        '''
    def has_chunk(self, dimension: Dimension, cx: int, cz: int) -> bool:
        """
        Is the chunk specified present in the level.

        :param dimension: The dimension of the chunk to check.
        :param cx: The chunk x coordinate.
        :param cz: The chunk z coordinate.
        :return: True if the chunk is present, False otherwise
        """
    def _raw_has_entry(self, key: DimensionCoordinates): ...
    def all_chunk_coords(self, dimension: Dimension) -> Set[Tuple[int, int]]:
        """
        The coordinates of every chunk in this world.

        This is the combination of chunks saved to the world and chunks yet to be saved.
        """
    def _all_entries(self, dimension: Dimension) -> Set[Tuple[int, int]]: ...
    def _raw_all_entries(self, dimension: Dimension) -> Iterable[Tuple[int, int]]: ...
    def get_chunk(self, dimension: Dimension, cx: int, cz: int) -> Chunk:
        """
        Gets the :class:`Chunk` object at the specified chunk coordinates.

        This may be a :class:`Chunk` instance if the chunk exists, None if it is known to not exist
        or :class:`~amulet.api.errors.ChunkDoesNotExist` will be raised if there is no record so it is unknown if it exists or not.

        Use has_chunk to check if there is a record of the chunk.

        :param dimension: The dimension to get the chunk from
        :param cx: The X coordinate of the desired chunk
        :param cz: The Z coordinate of the desired chunk
        :return: A Chunk instance or None
        :raises:
            :class:`~amulet.api.errors.ChunkDoesNotExist`: If the chunk does not exist (was deleted or never created)
        """
    def _raw_get_entry(self, key: EntryKeyType) -> EntryType: ...
    def put_chunk(self, chunk: Chunk, dimension: Dimension):
        """
        Add a given chunk to the chunk manager.

        :param chunk: The :class:`Chunk` to add to the chunk manager. It will be added at the location stored in :attr:`Chunk.coordinates`
        :param dimension: The dimension to add the chunk to.
        """
    def delete_chunk(self, dimension: Dimension, cx: int, cz: int):
        """
        Delete a chunk from the chunk manager.

        :param cx: The X coordinate of the chunk
        :param cz: The Z coordinate of the chunk
        :param dimension: The dimension to delete the chunk from.
        """
    def _create_new_revision_manager(self, key: EntryKeyType, original_entry: EntryType) -> RevisionManager: ...
