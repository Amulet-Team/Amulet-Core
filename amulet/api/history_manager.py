from __future__ import annotations

from typing import Dict, List, Tuple, Union, TYPE_CHECKING
import time
import os
import pickle
from .chunk import Chunk
if TYPE_CHECKING:
    from .world import ChunkCache


_ChunkLocation = Tuple[int, int, int]  # dimension, cx, cz

_ChunkRecord = Union[
    str,  # path to serialised file
    None  # chunk has been deleted
]

_ChunkStorage = List[  # change history of the chunk
    _ChunkRecord
]


class ChunkHistoryManager:
    """
    Class to manage changes and deletions of chunks
    """
    def __init__(self, temp_dir):
        self.temp_dir: str = temp_dir

        self._chunk_index = Dict[_ChunkLocation, int]  # the index of the current chunk in self._chunk_history
        self._chunk_history: Dict[
            _ChunkLocation,
            _ChunkStorage
        ] = {}

        self._snapshots: List[List[_ChunkLocation]] = []
        self._last_snapshot_time = 0.0

        self._snapshot_index = 0  # this is actually 1 more than the snapshot index
        self._last_save_snapshot = 0

    @property
    def undo_count(self) -> int:
        return self._snapshot_index

    @property
    def redo_count(self) -> int:
        return len(self._snapshots) - self._snapshot_index

    @property
    def unsaved_changes(self) -> int:
        """The number of changes that have been made since the last save"""
        return abs(self._snapshot_index - self._last_save_snapshot)

    def mark_saved(self):
        """Let the history manager know that the world has been saved"""
        self._last_save_snapshot = self._snapshot_index

    def add_original_chunk(self, chunk: Chunk, dimension: int):
        """Adds the given chunk to the chunk history"""
        # If the chunk does not exist in the chunk history then add it

        # This code is only called when loading a chunk from the database.
        # If this code is called and the chunk history already exists then the
        # chunk must have been unloaded from the World class and reloaded
        # only chunks that are unchanged or have been saved can be unloaded so
        # the latest chunk here should be the same as the one on disk
        if (dimension, chunk.cx, chunk.cz) not in self._chunk_history:
            self._chunk_index[(dimension, chunk.cx, chunk.cz)] = 0
            self._chunk_history[(dimension, chunk.cx, chunk.cz)] = [self._serialise_chunk(chunk, dimension, 0)]

    def create_snapshot(self, chunk_cache: 'ChunkCache'):
        """Find all the chunks which have changed since the last snapshot, serialise them and store the path to the file (or None if it has been deleted)"""
        snapshot = []
        for chunk_location, chunk in chunk_cache.items():
            assert chunk is None or isinstance(chunk, Chunk), 'Chunk must be None or a Chunk instance'
            if chunk is None or (chunk.changed and chunk.changed_time > self._last_snapshot_time):
                # if the chunk has been changed since the last shapshot add it to the new snapshot
                if chunk_location not in self._chunk_history:
                    # the chunk was added manually so the previous state was the chunk not existing
                    self._chunk_index[chunk_location] = 0
                    self._chunk_history[chunk_location] = [None]

                chunk_index = self._chunk_index[chunk_location]
                chunk_storage = self._chunk_history[chunk_location]
                if chunk is None:
                    # if the chunk has been deleted and the last save state was not also deleted update
                    if chunk_storage[chunk_index] is not None:
                        self._chunk_index[chunk_location] += 1
                        del chunk_storage[chunk_index+1:]
                        chunk_storage.append(None)
                        snapshot.append(chunk_location)
                else:
                    # updated the changed chunk
                    self._chunk_index[chunk_location] += 1
                    del chunk_storage[chunk_index + 1:]
                    chunk_storage[1].append(self._serialise_chunk(chunk, chunk_location[0], self._chunk_index[chunk_location]))
                    snapshot.append(chunk_location)

        if snapshot:
            # if there is data in the snapshot invalidate all newer snapshots and add to the database
            self._snapshot_index += 1
            del self._snapshots[self._snapshot_index:]
            self._snapshots.append(snapshot)
            self._last_snapshot_time = time.time()

    def _serialise_chunk(self, chunk: Union[Chunk, None], dimension: int, change_no: int) -> _ChunkRecord:
        """Serialise the chunk and write it to a file"""
        if chunk is None:
            return None

        os.makedirs(self.temp_dir, exist_ok=True)
        path = os.path.join(self.temp_dir, f'chunk.{dimension}.{chunk.cx}.{chunk.cz}.{change_no}.pickle')

        with open(path, "wb") as fp:
            pickle.dump(chunk, fp)

        return path

    def _unsearlise_chunk(self, dimension: int, cx: int, cz: int, change_offset: int) -> Union[Chunk, None]:
        """Load the next save state for a given chunk in a given direction"""
        chunk_location = (dimension, cx, cz)
        chunk_index = self._chunk_index[chunk_location] = self._chunk_index[chunk_location] + change_offset
        chunk_storage = self._chunk_history[chunk_location]
        assert 0 <= chunk_index < len(chunk_storage), 'Chunk index out of bounds'

        chunk = chunk_storage[chunk_index]
        if chunk is not None:
            with open(chunk, "rb") as fp:
                chunk = pickle.load(fp)
        return chunk

    def undo(self, chunk_cache: 'ChunkCache'):
        """Decrements the internal change index and un-serialises the last save state for each chunk changed"""
        if self._snapshot_index:
            # _snapshot_index == 1 is the first snapshot which is index 0 in self._snapshots
            self._snapshot_index -= 1
            snapshot = self._snapshots[self._snapshot_index]
            for chunk_location in snapshot:
                chunk = self._unsearlise_chunk(*chunk_location, -1)
                chunk_cache[chunk_location] = chunk

    def redo(self, chunk_cache: 'ChunkCache'):
        """Re-increments the internal change index and un-serialises the chunks from the next newest change"""
        if self._snapshot_index < len(self._snapshots):
            snapshot = self._snapshots[self._snapshot_index]
            self._snapshot_index += 1
            for chunk_location in snapshot:
                chunk = self._unsearlise_chunk(*chunk_location, 1)
                chunk_cache[chunk_location] = chunk
