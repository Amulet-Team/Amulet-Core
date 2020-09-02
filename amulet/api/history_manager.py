from __future__ import annotations

from typing import Dict, List, Tuple, Union, TYPE_CHECKING, Generator, Optional
import time
import os
from .chunk import Chunk
from amulet.api.data_types import (
    Dimension,
    DimensionCoordinates,  # dimension, cx, cz
)
from amulet.api.registry import BlockManager, BiomeManager

if TYPE_CHECKING:
    from .world import ChunkCache

ChunkRecord = Union[str, None]  # path to serialised file  # chunk has been deleted

ChunkStorage = List[ChunkRecord]  # change history of the chunk

ChunkIndex = Tuple[
    int,  # the index of the current chunk in ChunkStorage
    int,  # the index of the saved chunk in ChunkStorage. If these don't match the chunk has changed.
]


class ChunkHistoryManager:
    """
    Class to manage changes and deletions of chunks
    """

    def __init__(self, temp_dir):
        self.temp_dir: str = temp_dir

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

    def __contains__(self, item: DimensionCoordinates):
        return item in self._chunk_history

    @property
    def undo_count(self) -> int:
        return self._snapshot_index + 1

    @property
    def redo_count(self) -> int:
        return len(self._snapshots) - (self._snapshot_index + 1)

    @property
    def unsaved_changes(self) -> int:
        """The number of changes that have been made since the last save"""
        return (
            abs(self._snapshot_index - self._last_save_snapshot)
            + self._branch_save_count
        )

    def mark_saved(self):
        """Let the history manager know that the world has been saved"""
        self._last_save_snapshot = self._snapshot_index
        self._branch_save_count = 0
        # the current chunks have been saved to disk so update the saved chunk indexes
        for (
            chunk_location,
            (chunk_index, save_chunk_index),
        ) in self._chunk_index.items():
            self._chunk_index[chunk_location] = (chunk_index, chunk_index)

    def items(
        self, block_palette: BlockManager, biome_palette: BiomeManager
    ) -> Generator[Tuple[DimensionCoordinates, Optional[Chunk]], None, None]:
        for (dimension, cx, cz) in self._chunk_index.keys():
            yield (dimension, cx, cz), self.get_current(
                dimension, cx, cz, block_palette, biome_palette
            )

    def changed_chunks(self) -> Generator[DimensionCoordinates, None, None]:
        for chunk_location, (index, save_index) in self._chunk_index.items():
            if index != save_index:
                yield chunk_location

    def add_original_chunk(
        self, dimension: Dimension, cx: int, cz: int, chunk: Optional[Chunk]
    ):
        """Adds the given chunk to the chunk history"""
        # If the chunk does not exist in the chunk history then add it

        # This code is only called when loading a chunk from the database.
        # If this code is called and the chunk history already exists then the
        # chunk must have been unloaded from the World class and reloaded
        # only chunks that are unchanged or have been saved can be unloaded so
        # the latest chunk here should be the same as the one on disk

        if (dimension, cx, cz) not in self._chunk_history:
            if chunk is not None:
                assert cx == chunk.cx and cz == chunk.cz
            self._chunk_index[(dimension, cx, cz)] = (0, 0)
            self._chunk_history[(dimension, cx, cz)] = [
                self._serialise_chunk(chunk, dimension, 0)
            ]

    def create_undo_point(self, chunk_cache: "ChunkCache"):
        """Find all the chunks which have changed since the last snapshot, serialise them and store the path to the file (or None if it has been deleted)"""
        snapshot = []
        for chunk_location, chunk in list(chunk_cache.items()):
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
        self,
        dimension: Dimension,
        cx: int,
        cz: int,
        block_palette: BlockManager,
        biome_palette: BiomeManager,
        change_num_delta: int,
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
            chunk = Chunk.unpickle(chunk, block_palette, biome_palette)
        return chunk

    def undo(
        self,
        chunk_cache: "ChunkCache",
        chunk_palette: BlockManager,
        biome_palette: BiomeManager,
    ):
        """Decrements the internal change index and un-serialises the last save state for each chunk changed"""
        if self._snapshot_index >= 0:
            snapshot = self._snapshots[self._snapshot_index]
            for chunk_location in snapshot:
                dimension, cx, cz = chunk_location
                chunk = self._unserialise_chunk(
                    dimension, cx, cz, chunk_palette, biome_palette, -1
                )
                chunk_cache[chunk_location] = chunk
            self._snapshot_index -= 1

    def redo(
        self,
        chunk_cache: "ChunkCache",
        chunk_palette: BlockManager,
        biome_palette: BiomeManager,
    ):
        """Re-increments the internal change index and un-serialises the chunks from the next newest change"""
        if self._snapshot_index <= len(self._snapshots) - 2:
            snapshot = self._snapshots[self._snapshot_index + 1]
            for chunk_location in snapshot:
                dimension, cx, cz = chunk_location
                chunk = self._unserialise_chunk(
                    dimension, cx, cz, chunk_palette, biome_palette, 1
                )
                chunk_cache[chunk_location] = chunk
            self._snapshot_index += 1

    def get_current(
        self,
        dimension: Dimension,
        cx: int,
        cz: int,
        chunk_palette: BlockManager,
        biome_palette: BiomeManager,
    ):
        return self._unserialise_chunk(
            dimension, cx, cz, chunk_palette, biome_palette, 0
        )
