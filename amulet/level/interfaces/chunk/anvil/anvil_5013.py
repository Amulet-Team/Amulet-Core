from __future__ import annotations

from amulet.api.chunk import StatusFormats

from .anvil_5006 import (
    Anvil5006Interface as ParentInterface,
)


class Anvil5013Interface(ParentInterface):
    def __init__(self):
        super().__init__()
        self._set_feature("status", StatusFormats.Java_5013)

    @staticmethod
    def minor_is_valid(key: int):
        return 5013 <= key <= 5100


export = Anvil5013Interface
