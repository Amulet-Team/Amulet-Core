from typing import Union, BinaryIO

from .format_wrapper import BaseFormatWraper
from amulet.api.data_types import PathOrBuffer


class StructureFormatWrapper(BaseFormatWraper):
    def __init__(self, path_or_buffer: PathOrBuffer):
        super().__init__()
        self._path_or_buffer = path_or_buffer

    @property
    def path_or_buffer(self) -> PathOrBuffer:
        return self._path_or_buffer
