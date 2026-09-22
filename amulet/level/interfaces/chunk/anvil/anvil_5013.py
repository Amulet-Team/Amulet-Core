from __future__ import annotations

from .anvil_5006 import (
    Anvil5006Interface as ParentInterface,
)


class Anvil5013Interface(ParentInterface):
    @staticmethod
    def minor_is_valid(key: int):
        return 5013 <= key <= 5100


export = Anvil5013Interface
