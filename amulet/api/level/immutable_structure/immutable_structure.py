from __future__ import annotations
from typing import Generator

from ..base_level import BaseLevel
from .void_format_wrapper import VoidFormatWrapper
from amulet.api.chunk import Chunk
from amulet.api.data_types import Dimension
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.utils.generator import generator_unpacker
import copy


class ImmutableStructure(BaseLevel):
    """
    This is a special class that exists purely to hold chunk data and serialise it to the disk cache.
    There is no level attached to load or save chunks to.
    This class exists purely to store chunks in when copied from a level.
    The original wrapper is mutable so the chunks must be deep copied from it and dropped into here.
    """

    def __init__(
        self,
        temp_dir: str = None,
    ):
        super().__init__("", VoidFormatWrapper(""), temp_dir)
        self._selection = self._selection = SelectionGroup(
            [
                SelectionBox(
                    (-30_000_000, -30_000_000, -30_000_000),
                    (30_000_000, 30_000_000, 30_000_000),
                )
            ]
        )

    @property
    def selection_bounds(self) -> SelectionGroup:
        return self._selection

    def undo(self):
        pass

    def redo(self):
        pass

    def put_chunk(self, chunk: Chunk, dimension: Dimension):
        super().put_chunk(chunk, dimension)
        self.history_manager.create_undo_point()

    @classmethod
    def from_level(
        cls, level: BaseLevel, selection: SelectionGroup, dimension: Dimension
    ):
        return generator_unpacker(cls.from_level_iter(level, selection, dimension))

    @classmethod
    def from_level_iter(
        cls, level: BaseLevel, selection: SelectionGroup, dimension: Dimension
    ) -> Generator[float, None, ImmutableStructure]:
        """Populate this class with the chunks that intersect the selection."""
        self = cls()
        self._selection = selection.copy()
        dst_dimension = self.dimensions[0]
        count = len(list(level.get_coord_box(dimension, selection)))
        for index, (chunk, _) in enumerate(level.get_chunk_boxes(dimension, selection)):
            self.put_chunk(copy.deepcopy(chunk), dst_dimension)
            yield (index + 1) / count
        return self
