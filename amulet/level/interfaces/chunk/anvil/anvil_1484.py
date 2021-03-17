from __future__ import annotations

from .anvil_1467 import (
    Anvil1467Interface,
)


class Anvil1484Interface(Anvil1467Interface):
    def __init__(self):
        Anvil1467Interface.__init__(self)
        self.features["height_map"] = "C|V2"

    @staticmethod
    def minor_is_valid(key: int):
        return 1484 <= key < 1503


export = Anvil1484Interface
