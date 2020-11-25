# meta interface
from __future__ import annotations

from .anvil_1503 import (
    Anvil1503Interface,
)


class Anvil1908Interface(Anvil1503Interface):
    def __init__(self):
        Anvil1503Interface.__init__(self)
        self.features["height_map"] = "C|36LA|V4"

    @staticmethod
    def minor_is_valid(key: int):
        return 1908 <= key < 1912


export = Anvil1908Interface
