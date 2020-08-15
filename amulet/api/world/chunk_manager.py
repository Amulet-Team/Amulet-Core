from typing import Dict, Optional, Tuple, Union, List, Generator
import os
import time

from amulet.api.data_types import DimensionCoordinates, Dimension
from amulet.api.chunk import Chunk
from amulet.api.registry import BlockManager, BiomeManager
from amulet.api.errors import ChunkDoesNotExist

VoidChunk = None  # The chunk was deleted or it never existed.
ChunkCache = Dict[DimensionCoordinates, Union[Chunk, VoidChunk]]

ChunkRecord = Union[str, None]  # path to serialised file  # chunk has been deleted

ChunkStorage = List[ChunkRecord]  # change history of the chunk

ChunkIndex = Tuple[
    int,  # the index of the current chunk in ChunkStorage
    int,  # the index of the saved chunk in ChunkStorage. If these don't match the chunk has changed.
]


class ChunkManager:
    """The ChunkManager class is a class that handles chunks within a world.
    It handles the temporary database of chunks in RAM that can be directly modified.
    It handles a serialised version of the chunks on disk to reduce RAM usage.
    It also contains a history manager to allow undoing and redoing of changes."""

    def __init__(
        self, temp_dir: str, chunk_palette: BlockManager, biome_palette: BiomeManager,
    ):
        self._block_palette: BlockManager = chunk_palette
        self._biome_palette: BiomeManager = biome_palette
        self._chunk_cache: ChunkCache = {}  # The storage of Chunks in RAM

        self.temp_dir: str = temp_dir  # the location to serialise Chunks to
        self._chunk_index: Dict[
            DimensionCoordinates, ChunkIndex
        ] = {}  # the indexes into self._chunk_history
        self._chunk_history: Dict[DimensionCoordinates, ChunkStorage] = {}

        self._snapshots: List[List[DimensionCoordinates]] = []
        self._last_snapshot_time = 0.0

        self._snapshot_index = -1

        # the snapshot that was saved or the save branches off from
        self._last_save_snapshot = -1
        self._branch_save_count = 0  # if the user saves, undoes and does a new operation a save branch will be lost
        # This is the number of changes on that branch

    @property
    def changed(self) -> bool:
        """Has any data been modified but not saved to disk"""
        for chunk_location, chunk in self._chunk_cache.items():
            if chunk is None:
                # if the chunk is None and the saved record is not None, the chunk has changed.
                if chunk_location not in self._chunk_index:
                    return True
                _, save_chunk_index = self._chunk_index[chunk_location]
                chunk_storage = self._chunk_history[chunk_location]
                if chunk_storage[save_chunk_index] is not None:
                    return True
            elif chunk.changed:
                return True
        for chunk_index, save_chunk_index in self._chunk_index.values():
            if chunk_index != save_chunk_index:
                return True
        return False

    def changed_chunks(self) -> Generator[DimensionCoordinates, None, None]:
        """The location of every chunk that has been changed since the last save."""
        changed_chunks = set()
        for chunk_location, chunk in self._chunk_cache.items():
            if chunk is None:
                # if the chunk is None and the saved record is not None, the chunk has changed.
                if chunk_location in self._chunk_index:
                    _, save_chunk_index = self._chunk_index[chunk_location]
                    chunk_storage = self._chunk_history[chunk_location]
                    if chunk_storage[save_chunk_index] is not None:
                        changed_chunks.add(chunk_location)
                        yield chunk_location
                else:
                    changed_chunks.add(chunk_location)
                    yield chunk_location

            elif chunk.changed:
                changed_chunks.add(chunk_location)
                yield chunk_location
        for chunk_location, (index, save_index) in self._chunk_index.items():
            if index != save_index and chunk_location not in changed_chunks:
                yield chunk_location

    def create_undo_point(self) -> bool:
        """Find all the chunks which have changed since the last snapshot, serialise them and store the path to the file (or None if it has been deleted)"""
        snapshot = []
        for chunk_location, chunk in list(self._chunk_cache.items()):
            assert chunk is None or isinstance(
                chunk, Chunk
            ), "Chunk must be None or a Chunk instance"
            if chunk is None or chunk.changed:
                # if the chunk has been changed since the last shapshot add it to the new snapshot
                if chunk_location not in self._chunk_history:
                    # the chunk was added manually so the previous state was the chunk not existing
                    self._chunk_index[chunk_location] = (0, 0)
                    self._chunk_history[chunk_location] = [None]

                chunk_index, save_chunk_index = self._chunk_index[chunk_location]
                chunk_storage = self._chunk_history[chunk_location]
                if chunk is None:
                    # if the chunk has been deleted and the last save state was not also deleted update
                    if chunk_storage[chunk_index] is not None:
                        self._chunk_index[chunk_location] = (
                            chunk_index + 1,
                            save_chunk_index,
                        )
                        del chunk_storage[
                            chunk_index + 1 :
                        ]  # delete any upstream chunks
                        chunk_storage.append(None)
                        snapshot.append(chunk_location)
                else:
                    # updated the changed chunk
                    self._chunk_index[chunk_location] = (
                        chunk_index + 1,
                        save_chunk_index,
                    )
                    del chunk_storage[chunk_index + 1 :]
                    chunk_storage.append(
                        self._serialise_chunk(chunk, chunk_location[0], chunk_index + 1)
                    )
                    snapshot.append(chunk_location)
                    chunk.changed = False

        if snapshot:
            # if there is data in the snapshot invalidate all newer snapshots and add to the database
            if self._last_save_snapshot > self._snapshot_index:
                self._branch_save_count += (
                    self._last_save_snapshot - self._snapshot_index
                )
                self._last_save_snapshot = self._snapshot_index
            self._snapshot_index += 1
            del self._snapshots[self._snapshot_index :]
            self._snapshots.append(snapshot)
            self._last_snapshot_time = time.time()
            return True
        return False

    def unload(self, safe_area: Optional[Tuple[Dimension, int, int, int, int]] = None):
        """Unload all chunks not in the safe area from the temporary database
        Safe area format: dimension, min chunk X|Z, max chunk X|Z"""
        unload_chunks = []
        if safe_area is None:
            unload_chunks = list(self._chunk_cache.keys())
        else:
            dimension, minx, minz, maxx, maxz = safe_area
            for (cd, cx, cz), chunk in self._chunk_cache.items():
                if not (cd == dimension and minx <= cx <= maxx and minz <= cz <= maxz):
                    unload_chunks.append((cd, cx, cz))
        for chunk_key in unload_chunks:
            del self._chunk_cache[chunk_key]

    def has_chunk(self, dimension: Dimension, cx: int, cz: int) -> bool:
        """Does the ChunkManager have the chunk specified"""
        key = (dimension, cx, cz)
        return key in self._chunk_cache or key in self._chunk_history

    def __contains__(self, item: DimensionCoordinates):
        return self.has_chunk(*item)

    def get_chunk(self, dimension: Dimension, cx: int, cz: int) -> Optional[Chunk]:
        """
        Gets the chunk object at the specified chunk coordinates.
        This may be a Chunk instance if the chunk exists, None if it is known to not exist
        or ChunkDoesNotExist will be raised if there is no record so it is unknown if it exists or not.
        Use has_chunk to check if there is a record of the chunk.

        :param dimension: The dimension to get the chunk from
        :param cx: The X coordinate of the desired chunk
        :param cz: The Z coordinate of the desired chunk
        :return: A Chunk instance or None
        :raises: ChunkDoesNotExist if there is no record of the chunk.
        """
        chunk_key = (dimension, cx, cz)
        if chunk_key in self._chunk_cache:
            chunk = self._chunk_cache[chunk_key]
        elif chunk_key in self._chunk_history:
            chunk = self._chunk_cache[chunk_key] = self.get_current(dimension, cx, cz)
        else:
            raise ChunkDoesNotExist
        return chunk

    def put_original_chunk(
        self, dimension: Dimension, cx: int, cz: int, chunk: Optional[Chunk]
    ):
        """Adds the original Chunk to the chunk database"""
        # If the chunk does not exist in the chunk history then add it

        # This code is only called when loading a chunk from the database.
        # If this code is called and the chunk history already exists then the
        # chunk must have been unloaded from the World class and reloaded
        # only chunks that are unchanged or have been saved can be unloaded so
        # the latest chunk here should be the same as the one on disk

        key = (dimension, cx, cz)
        if key not in self._chunk_history:
            if chunk is not None:
                assert cx == chunk.cx and cz == chunk.cz
            self._chunk_index[key] = (0, 0)
            self._chunk_history[key] = [self._serialise_chunk(chunk, dimension, 0)]
            self._chunk_cache[key] = chunk

    def put_chunk(self, chunk: Chunk, dimension: Dimension):
        """Add a chunk to the universal world database"""
        chunk.changed = True
        chunk.block_palette = self._block_palette
        chunk.biome_palette = self._biome_palette
        self._chunk_cache[(dimension, chunk.cx, chunk.cz)] = chunk

    def delete_chunk(self, dimension: Dimension, cx: int, cz: int):
        """Delete a chunk from the universal world database"""
        self._chunk_cache[(dimension, cx, cz)] = None

    def undo(self):
        """Undoes the last set of changes to the chunks"""
        if self._snapshot_index >= 0:
            snapshot = self._snapshots[self._snapshot_index]
            for chunk_location in snapshot:
                dimension, cx, cz = chunk_location
                chunk = self._unserialise_chunk(dimension, cx, cz, -1)
                self._chunk_cache[chunk_location] = chunk
            self._snapshot_index -= 1

    @property
    def undo_count(self) -> int:
        return self._snapshot_index + 1

    def redo(self):
        """Redoes the last set of changes to the chunks"""
        if self._snapshot_index <= len(self._snapshots) - 2:
            snapshot = self._snapshots[self._snapshot_index + 1]
            for chunk_location in snapshot:
                dimension, cx, cz = chunk_location
                chunk = self._unserialise_chunk(dimension, cx, cz, 1)
                self._chunk_cache[chunk_location] = chunk
            self._snapshot_index += 1

    @property
    def redo_count(self) -> int:
        return len(self._snapshots) - (self._snapshot_index + 1)

    def restore_last_undo_point(self):
        """Restore the world to the state it was when self.create_undo_point was called.
        If an operation errors there may be modifications made that did not get tracked.
        This will revert those changes."""
        self.unload()

    @property
    def unsaved_changes(self) -> int:
        """The number of changes that have been made since the last save"""
        return (
            abs(self._snapshot_index - self._last_save_snapshot)
            + self._branch_save_count
        )

    def mark_saved(self):
        """Let the chunk manager know that the world has been saved"""
        self._last_save_snapshot = self._snapshot_index
        self._branch_save_count = 0
        # the current chunks have been saved to disk so update the saved chunk indexes
        for (
            chunk_location,
            (chunk_index, save_chunk_index),
        ) in self._chunk_index.items():
            self._chunk_index[chunk_location] = (chunk_index, chunk_index)

    def _serialise_chunk(
        self, chunk: Union[Chunk, None], dimension: Dimension, change_no: int
    ) -> ChunkRecord:
        """Serialise the chunk and write it to a file"""
        if chunk is None:
            return None

        os.makedirs(self.temp_dir, exist_ok=True)
        path = os.path.join(
            self.temp_dir,
            f"chunk.{dimension}.{chunk.cx}.{chunk.cz}.{change_no}.pickle.gz",
        )

        chunk.pickle(path)

        return path

    def _unserialise_chunk(
        self, dimension: Dimension, cx: int, cz: int, change_num_delta: int,
    ) -> Union[Chunk, None]:
        """Load the next save state for a given chunk in a given direction"""
        chunk_location = (dimension, cx, cz)
        chunk_index, save_chunk_index = self._chunk_index[chunk_location]
        chunk_index += change_num_delta
        self._chunk_index[chunk_location] = (chunk_index, save_chunk_index)
        chunk_storage = self._chunk_history[chunk_location]
        assert 0 <= chunk_index < len(chunk_storage), "Chunk index out of bounds"

        chunk = chunk_storage[chunk_index]
        if chunk is not None:
            chunk = Chunk.unpickle(chunk, self._block_palette, self._biome_palette)
        return chunk

    def get_current(self, dimension: Dimension, cx: int, cz: int):
        return self._unserialise_chunk(dimension, cx, cz, 0)
