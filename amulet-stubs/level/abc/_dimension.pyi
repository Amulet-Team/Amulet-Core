import abc
from ._chunk_handle import ChunkHandle as ChunkHandle, ChunkKey as ChunkKey
from ._history import HistoryManagerLayer as HistoryManagerLayer
from ._level import LevelFriend as LevelFriend, LevelPrivateT as LevelPrivateT
from ._raw_level import RawDimension as RawDimension
from abc import ABC, abstractmethod
from amulet.api.data_types import DimensionID as DimensionID
from amulet.biome import Biome as Biome
from amulet.block import BlockStack as BlockStack
from amulet.selection import SelectionGroup as SelectionGroup
from threading import Lock
from typing import Generic, TypeVar
from weakref import WeakValueDictionary

ChunkHandleT = TypeVar('ChunkHandleT', bound=ChunkHandle)

class Dimension(LevelFriend[LevelPrivateT], ABC, Generic[LevelPrivateT, ChunkHandleT], metaclass=abc.ABCMeta):
    _dimension: DimensionID
    _chunk_handles: WeakValueDictionary[tuple[int, int], ChunkHandleT]
    _chunk_handle_lock: Lock
    _chunk_history: HistoryManagerLayer[ChunkKey]
    _raw: RawDimension
    def __init__(self, level_data: LevelPrivateT, dimension: DimensionID) -> None: ...
    @property
    def dimension(self) -> DimensionID: ...
    def bounds(self) -> SelectionGroup:
        """The editable region of the dimension."""
    def default_block(self) -> BlockStack:
        """The default block for this dimension"""
    def default_biome(self) -> Biome:
        """The default biome for this dimension"""
    def chunk_coords(self) -> set[tuple[int, int]]:
        """
        The coordinates of every chunk that exists in this dimension.

        This is the combination of chunks saved to the level and chunks yet to be saved.
        """
    def changed_chunk_coords(self) -> set[tuple[int, int]]:
        """The coordinates of every chunk in this dimension that have been changed since the last save."""
    @abstractmethod
    def _create_chunk_handle(self, cx: int, cz: int) -> ChunkHandleT: ...
    def get_chunk_handle(self, cx: int, cz: int) -> ChunkHandleT: ...
