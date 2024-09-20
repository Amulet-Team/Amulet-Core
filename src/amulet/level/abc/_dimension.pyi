import abc
from abc import ABC
from typing import Callable, Generic, TypeVar

from amulet.biome import Biome as Biome
from amulet.block import BlockStack as BlockStack
from amulet.data_types import DimensionId as DimensionId
from amulet.selection import SelectionGroup as SelectionGroup

from ._chunk_handle import ChunkHandle as ChunkHandle
from ._chunk_handle import ChunkKey as ChunkKey
from ._history import HistoryManagerLayer as HistoryManagerLayer
from ._level import LevelFriend as LevelFriend
from ._level import LevelT as LevelT
from ._raw_level import RawDimension as RawDimension

ChunkHandleT = TypeVar("ChunkHandleT", bound=ChunkHandle)
RawDimensionT = TypeVar("RawDimensionT", bound=RawDimension)

class Dimension(
    LevelFriend[LevelT],
    ABC,
    Generic[LevelT, RawDimensionT, ChunkHandleT],
    metaclass=abc.ABCMeta,
):
    def __init__(
        self, level_ref: Callable[[], LevelT | None], dimension_id: DimensionId
    ) -> None: ...
    @property
    def dimension_id(self) -> DimensionId: ...
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

    def get_chunk_handle(self, cx: int, cz: int) -> ChunkHandleT: ...
