from __future__ import annotations

from .anvil_1908 import (
    Anvil1908Interface,
)


class Anvil1912Interface(Anvil1908Interface):
    def __init__(self):
        Anvil1908Interface.__init__(self)
        self.features["status"] = "j14"

    @staticmethod
    def minor_is_valid(key: int):
        return 1912 <= key < 1934


export = Anvil1912Interface
