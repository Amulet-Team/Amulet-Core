from typing import Optional, BinaryIO, List, Any, Union

from .format_wrapper import FormatWrapper
from amulet.api.data_types import Dimension
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet import log


class StructureFormatWrapper(FormatWrapper):
    """A base FormatWrapper for all structures that only have one dimension."""

    def __init__(
        self,
        path: str,
        buffer: Optional[BinaryIO] = None
    ):
        super().__init__(path)

    @property
    def dimensions(self) -> List[Dimension]:
        return ["main"]

    @property
    def can_add_dimension(self) -> bool:
        return False

    def register_dimension(self, dimension_internal: Any, dimension_name: Dimension):
        pass

    @property
    def requires_selection(self) -> bool:
        """Does this object require that a selection be defined when creating it from scratch?"""
        return True
