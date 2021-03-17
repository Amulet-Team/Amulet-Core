# meta interface
from __future__ import annotations

from .anvil_1912 import (
    Anvil1912Interface,
)


class Anvil1934Interface(Anvil1912Interface):
    def __init__(self):
        Anvil1912Interface.__init__(self)
        self.features["light_optional"] = "true"

    @staticmethod
    def minor_is_valid(key: int):
        return 1934 <= key < 2203


export = Anvil1934Interface
