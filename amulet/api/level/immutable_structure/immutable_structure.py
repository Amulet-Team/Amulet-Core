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
    This is a special version of the level class that is only used when extracting a region of the world.

    It is much the same as a normal level class but does not have an associated file/folder data like :class:`~amulet.api.level.World` and :class:`~amulet.api.level.Structure` do.

    To extract a section of a world you should use :meth:`~amulet.api.level.BaseLevel.extract_structure`.
    """

    def __init__(
        self,
    ):
        """
        Construct an :class:`ImmutableStructure` instance.

        You probably don't want to call this directly.

        To extract a section of a world you should use :meth:`~amulet.api.level.BaseLevel.extract_structure`.
        """
        super().__init__("", VoidFormatWrapper(""))
        self._selection = SelectionGroup(
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

    def bounds(self, dimension: Dimension) -> SelectionGroup:
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
        """
        Extract a section of the level into an :class:`ImmutableStructure` class.

        :param level: The level to extract the area from.
        :param selection: The selection to extract.
        :param dimension: The dimension to extract from.
        :return: The created instance of :class:`ImmutableStructure`
        """
        return generator_unpacker(cls.from_level_iter(level, selection, dimension))

    @classmethod
    def from_level_iter(
        cls, level: BaseLevel, selection: SelectionGroup, dimension: Dimension
    ) -> Generator[float, None, ImmutableStructure]:
        """
        Extract a section of the level into an :class:`ImmutableStructure` class.

        Also yields the progress from 0-1.

        :param level: The level to extract the area from.
        :param selection: The selection to extract.
        :param dimension: The dimension to extract from.
        :return: The created instance of :class:`ImmutableStructure`
        """
        self = cls()
        self._selection = selection
        dst_dimension = self.dimensions[0]
        count = len(list(level.get_coord_box(dimension, selection)))
        for index, (chunk, _) in enumerate(level.get_chunk_boxes(dimension, selection)):
            self.put_chunk(copy.deepcopy(chunk), dst_dimension)
            yield (index + 1) / count
        return self
