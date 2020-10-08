from typing import Optional, BinaryIO, List, Any, Union

from .format_wrapper import FormatWrapper
from amulet.api.data_types import PathOrBuffer
from amulet.api.data_types import Dimension
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet import log


class StructureFormatWrapper(FormatWrapper):
    def __init__(self, path_or_buffer: PathOrBuffer):
        super().__init__()
        self._path_or_buffer = path_or_buffer

    @property
    def dimensions(self) -> List[Dimension]:
        return ["main"]

    @property
    def can_add_dimension(self) -> bool:
        return False

    def register_dimension(
            self, dimension_internal: Any, dimension_name: Dimension
    ):
        pass

    @property
    def mutable_selection(self) -> bool:
        """Can the selection be modified."""
        return True

    @property
    def selection(self) -> SelectionGroup:
        return self._selection.copy()

    @selection.setter
    def selection(self, selection: Union[SelectionGroup, SelectionBox]):
        if isinstance(selection, SelectionBox):
            self._selection = SelectionGroup([selection])
        elif isinstance(selection, SelectionGroup):
            box_count = len(selection)
            if box_count == 0:
                raise ValueError("no box was given")
            elif box_count > 1:
                if self.multi_selection:
                    self._selection = SelectionGroup([selection.selection_boxes[0]])
                else:
                    log.error(f"{box_count} boxes given but this structure can only accept one.")
            else:
                self._selection = selection
        else:
            raise TypeError(f"selection type {type(selection)} is invalid.")

