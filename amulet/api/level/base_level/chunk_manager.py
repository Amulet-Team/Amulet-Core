from __future__ import annotations
from typing import Optional, Tuple, Generator, Set, Iterable, Dict
import weakref

from amulet.api.data_types import DimensionCoordinates, Dimension
from amulet.api.chunk import Chunk
from amulet.api.history.data_types import EntryType, EntryKeyType
from amulet.api.history.base import RevisionManager
from amulet.api.history.revision_manager import DBRevisionManager
from amulet.api.errors import ChunkDoesNotExist, ChunkLoadError
from amulet.api.history.history_manager import DatabaseHistoryManager
from amulet.api.cache import get_cache_db
from amulet.api import level as api_level


class ChunkDBEntry(DBRevisionManager):
    __slots__ = ("_world",)

    def __init__(
        self, world: api_level.BaseLevel, prefix: str, initial_state: EntryType
    ):
        super().__init__(prefix, initial_state)
        self._world = weakref.ref(world)

    @property
    def world(self) -> api_level.BaseLevel:
        return self._world()

    def _serialise(self, path: str, entry: Optional[Chunk]) -> Optional[str]:
        if entry is None:
            return None
        else:
            pickled_bytes = entry.pickle()
            get_cache_db().put(path.encode("utf-8"), pickled_bytes)
            return path

    def _deserialise(self, path: Optional[str]) -> Optional[Chunk]:
        if path is None:
            return None
        else:
            pickled_bytes = get_cache_db().get(path.encode("utf-8"))
            return Chunk.unpickle(
                pickled_bytes, self.world.block_palette, self.world.biome_palette
            )


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

    def __init__(self, prefix: str, level: api_level.BaseLevel):
        """
        Construct a :class:`ChunkManager` instance.

        Should not be directly used by third party code.

        :param prefix: The prefix to store data under in the database. Must be unique to the world.
        :param level: The world that this chunk manager is associated with
        """
        super().__init__()
        self._prefix: str = f"{prefix}/chunks"  # the location to serialise Chunks to
        self._level = weakref.ref(level)

    @property
    def level(self) -> api_level.BaseLevel:
        """The level that this chunk manager is associated with."""
        return self._level()

    def changed_chunks(self) -> Generator[DimensionCoordinates, None, None]:
        """The location of every chunk that has been changed since the last save."""
        yield from self.changed_entries()

    def unload(self, safe_area: Optional[Tuple[Dimension, int, int, int, int]] = None):
        """
        Unload all chunks from the temporary database that are not in the safe area.

        :param safe_area: The area that should not be unloaded [dimension, min_chunk_x, min_chunk_z, max_chunk_x, max_chunk_z]. If None will unload all chunk data.
        """
        with self._lock:
            if safe_area is None:
                self._temporary_database.clear()
            else:
                unload_chunks = []
                dimension, minx, minz, maxx, maxz = safe_area
                for (cd, cx, cz), chunk in self._temporary_database.items():
                    if not (
                        cd == dimension and minx <= cx <= maxx and minz <= cz <= maxz
                    ):
                        unload_chunks.append((cd, cx, cz))
                for chunk_key in unload_chunks:
                    del self._temporary_database[chunk_key]

    def __contains__(self, item: DimensionCoordinates) -> bool:
        """
        Is the chunk specified present in the level.

        >>> ("minecraft:overworld", 0, 0) in level.chunks
        True

        :param item: A tuple of dimension, chunk x coordinate and chunk z coordinate.
        :return: True if the chunk is present, False otherwise
        """
        return self._has_entry(item)

    def has_chunk(self, dimension: Dimension, cx: int, cz: int) -> bool:
        """
        Is the chunk specified present in the level.

        :param dimension: The dimension of the chunk to check.
        :param cx: The chunk x coordinate.
        :param cz: The chunk z coordinate.
        :return: True if the chunk is present, False otherwise
        """
        return self._has_entry((dimension, cx, cz))

    def _raw_has_entry(self, key: DimensionCoordinates):
        dimension, cx, cz = key
        return self.level.level_wrapper.has_chunk(cx, cz, dimension)

    def all_chunk_coords(self, dimension: Dimension) -> Set[Tuple[int, int]]:
        """
        The coordinates of every chunk in this world.

        This is the combination of chunks saved to the world and chunks yet to be saved.
        """
        return self._all_entries(dimension)

    def _all_entries(self, dimension: Dimension) -> Set[Tuple[int, int]]:
        # custom behaviour to handle the dimension option.
        with self._lock:
            coords = set()
            deleted_chunks = set()
            for key in self._temporary_database.keys():
                dim, cx, cz = key
                if dim == dimension:
                    if self._temporary_database[key] is None:
                        deleted_chunks.add((cx, cz))
                    else:
                        coords.add((cx, cz))

            for key in self._history_database.keys():
                dim, cx, cz = key
                if dim == dimension and key not in self._temporary_database:
                    if self._history_database[key].is_deleted:
                        deleted_chunks.add((cx, cz))
                    else:
                        coords.add((cx, cz))

            for key in self._raw_all_entries(dimension):
                if key not in coords and key not in deleted_chunks:
                    coords.add(key)

        return coords

    def _raw_all_entries(self, dimension: Dimension) -> Iterable[Tuple[int, int]]:
        return self.level.level_wrapper.all_chunk_coords(dimension)

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
        return self._get_entry((dimension, cx, cz))

    def _raw_get_entry(self, key: EntryKeyType) -> EntryType:
        dimension, cx, cz = key
        chunk = self.level.level_wrapper.load_chunk(cx, cz, dimension)
        chunk.block_palette = self.level.block_palette
        chunk.biome_palette = self.level.biome_palette
        return chunk

    def put_chunk(self, chunk: Chunk, dimension: Dimension):
        """
        Add a given chunk to the chunk manager.

        :param chunk: The :class:`Chunk` to add to the chunk manager. It will be added at the location stored in :attr:`Chunk.coordinates`
        :param dimension: The dimension to add the chunk to.
        """
        chunk.block_palette = self.level.block_palette
        chunk.biome_palette = self.level.biome_palette
        self._put_entry((dimension, chunk.cx, chunk.cz), chunk)

    def delete_chunk(self, dimension: Dimension, cx: int, cz: int):
        """
        Delete a chunk from the chunk manager.

        :param cx: The X coordinate of the chunk
        :param cz: The Z coordinate of the chunk
        :param dimension: The dimension to delete the chunk from.
        """
        self._delete_entry((dimension, cx, cz))

    def _create_new_revision_manager(
        self, key: EntryKeyType, original_entry: EntryType
    ) -> RevisionManager:
        dimension, cx, cz = key
        prefix = f"{self._prefix}/{dimension}/{cx}.{cz}"
        return ChunkDBEntry(self.level, prefix, original_entry)
