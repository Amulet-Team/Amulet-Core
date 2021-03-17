# meta interface
from __future__ import annotations

from .anvil_1444 import (
    Anvil1444Interface,
)


class Anvil1466Interface(Anvil1444Interface):
    def __init__(self):
        Anvil1444Interface.__init__(self)
        self.features["height_map"] = "C|V1"

    @staticmethod
    def minor_is_valid(key: int):
        return 1466 <= key < 1467


export = Anvil1466Interface
