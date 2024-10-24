from __future__ import annotations

from .anvil_2844 import (
    Anvil2844Interface as ParentInterface,
)
from amulet.api.chunk import StatusFormats


class Anvil3463Interface(ParentInterface):
    def __init__(self):
        super().__init__()
        self._set_feature("status", StatusFormats.Java_20)

    @staticmethod
    def minor_is_valid(key: int):
        return 3454 <= key <= 4100


export = Anvil3463Interface
