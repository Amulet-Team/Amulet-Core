from ..base_level import BaseLevel as BaseLevel
from .void_format_wrapper import VoidFormatWrapper as VoidFormatWrapper
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import Dimension as Dimension
from amulet.selection import SelectionBox as SelectionBox, SelectionGroup as SelectionGroup
from amulet.utils.generator import generator_unpacker as generator_unpacker
from typing import Generator

class ImmutableStructure(BaseLevel):
    """
    This is a special version of the level class that is only used when extracting a region of the world.

    It is much the same as a normal level class but does not have an associated file/folder data like :class:`~amulet.api.level.World` and :class:`~amulet.api.level.Structure` do.

    To extract a section of a world you should use :meth:`~amulet.api.level.BaseLevel.extract_structure`.
    """
    _selection: Incomplete
    def __init__(self) -> None:
        """
        Construct an :class:`ImmutableStructure` instance.

        You probably don't want to call this directly.

        To extract a section of a world you should use :meth:`~amulet.api.level.BaseLevel.extract_structure`.
        """
    @property
    def selection_bounds(self) -> SelectionGroup: ...
    def bounds(self, dimension: Dimension) -> SelectionGroup: ...
    def undo(self) -> None: ...
    def redo(self) -> None: ...
    def put_chunk(self, chunk: Chunk, dimension: Dimension): ...
    @classmethod
    def from_level(cls, level: BaseLevel, selection: SelectionGroup, dimension: Dimension):
        """
        Extract a section of the level into an :class:`ImmutableStructure` class.

        :param level: The level to extract the area from.
        :param selection: The selection to extract.
        :param dimension: The dimension to extract from.
        :return: The created instance of :class:`ImmutableStructure`
        """
    @classmethod
    def from_level_iter(cls, level: BaseLevel, selection: SelectionGroup, dimension: Dimension) -> Generator[float, None, ImmutableStructure]:
        """
        Extract a section of the level into an :class:`ImmutableStructure` class.

        Also yields the progress from 0-1.

        :param level: The level to extract the area from.
        :param selection: The selection to extract.
        :param dimension: The dimension to extract from.
        :return: The created instance of :class:`ImmutableStructure`
        """
