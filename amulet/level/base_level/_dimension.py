from abc import ABC, abstractmethod

from weakref import WeakValueDictionary
from threading import Lock

from amulet.api.data_types import BiomeType, DimensionID
from amulet.api.block import Block
from amulet.api.selection import SelectionGroup

from ._level import LevelFriend, BaseLevelPrivate
from ._history import HistoryManagerLayer
from ._chunk_handle import ChunkKey, ChunkHandle


class Dimension(LevelFriend, ABC):
    _dimension: DimensionID
    _chunk_handles: WeakValueDictionary[tuple[int, int], ChunkHandle]
    _chunk_handle_lock: Lock
    _chunk_history: HistoryManagerLayer[ChunkKey]

    def __init__(self, level_data: BaseLevelPrivate, dimension: DimensionID):
        super().__init__(level_data)
        self._dimension = dimension
        self._chunk_handles = WeakValueDictionary()
        self._chunk_handle_lock = Lock()
        self._chunk_history = self._l.history_manager.new_layer()

    @property
    def dimension(self) -> DimensionID:
        return self._dimension

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

    def chunk_coords(self) -> set[tuple[int, int]]:
        """
        The coordinates of every chunk that exists in this dimension.

        This is the combination of chunks saved to the level and chunks yet to be saved.
        """
        chunks: set[tuple[int, int]] = set()  # TODO: pull the data from the raw level
        for key, state in self._chunk_history.resources_exist_map().items():
            if state:
                chunks.add((key.cx, key.cz))
            else:
                chunks.discard((key.cx, key.cz))
        return chunks

    def changed_chunk_coords(self) -> set[tuple[int, int]]:
        """The coordinates of every chunk in this dimension that have been changed since the last save."""
        return {(key.cx, key.cz) for key in self._chunk_history.changed_resources()}

    def get_chunk_handle(self, cx: int, cz: int) -> ChunkHandle:
        key = cx, cz
        with self._chunk_handle_lock:
            chunk_handle = self._chunk_handles.get(key)
            if chunk_handle is None:
                chunk_handle = self._chunk_handles[key] = ChunkHandle(
                    self._l, self._chunk_history, self._dimension, cx, cz
                )
            return chunk_handle
