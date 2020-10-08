from typing import Optional, BinaryIO, List, Any, Union

from .format_wrapper import FormatWrapper
from amulet.api.data_types import PathOrBuffer
from amulet.api.data_types import Dimension


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
    def path_or_buffer(self) -> PathOrBuffer:
        return self._path_or_buffer
