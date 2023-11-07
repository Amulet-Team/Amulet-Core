from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from weakref import WeakValueDictionary
from threading import Lock

from amulet.api.data_types import BiomeType, DimensionID
from amulet.block import Block
from amulet.selection import SelectionGroup

from ._level import LevelFriend, LevelPrivateT
from ._history import HistoryManagerLayer
from ._chunk_handle import ChunkKey, ChunkHandleT
from ._raw_level import RawDimensionT


class AbstractDimension(LevelFriend[LevelPrivateT], Generic[LevelPrivateT, RawDimensionT, ChunkHandleT], ABC):
    _dimension: DimensionID
    _chunk_handles: WeakValueDictionary[tuple[int, int], ChunkHandleT]
    _chunk_handle_lock: Lock
    _chunk_history: HistoryManagerLayer[ChunkKey]
    _raw: RawDimensionT

    def __init__(self, level_data: LevelPrivateT, dimension: DimensionID):
        super().__init__(level_data)
        self._dimension = dimension
        self._chunk_handles = WeakValueDictionary()
        self._chunk_handle_lock = Lock()
        self._chunk_history = self._l.history_manager.new_layer()
        self._raw = self._l.level.raw.get_dimension(self._dimension)

    @property
    def dimension(self) -> DimensionID:
        return self._dimension

    def bounds(self) -> SelectionGroup:
        """The editable region of the dimension."""
        return self._raw.bounds()

    def default_block(self) -> Block:
        """The default block for this dimension"""
        return self._raw.default_block()

    def default_biome(self) -> BiomeType:
        """The default biome for this dimension"""
        return self._raw.default_biome()

    def chunk_coords(self) -> set[tuple[int, int]]:
        """
        The coordinates of every chunk that exists in this dimension.

        This is the combination of chunks saved to the level and chunks yet to be saved.
        """
        chunks: set[tuple[int, int]] = set(self._raw.all_chunk_coords())
        for key, state in self._chunk_history.resources_exist_map().items():
            if state:
                chunks.add((key.cx, key.cz))
            else:
                chunks.discard((key.cx, key.cz))
        return chunks

    def changed_chunk_coords(self) -> set[tuple[int, int]]:
        """The coordinates of every chunk in this dimension that have been changed since the last save."""
        return {(key.cx, key.cz) for key in self._chunk_history.changed_resources()}

    @abstractmethod
    def _create_chunk_handle(self, cx: int, cz: int) -> ChunkHandleT:
        raise NotImplementedError

    def get_chunk_handle(self, cx: int, cz: int) -> ChunkHandleT:
        key = cx, cz
        with self._chunk_handle_lock:
            chunk_handle = self._chunk_handles.get(key)
            if chunk_handle is None:
                chunk_handle = self._chunk_handles[key] = self._create_chunk_handle(
                    cx, cz
                )
            return chunk_handle