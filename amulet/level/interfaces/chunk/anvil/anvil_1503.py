from __future__ import annotations

from .anvil_1484 import (
    Anvil1484Interface,
)


class Anvil1503Interface(Anvil1484Interface):
    """
    Changed height keys again
    """

    def __init__(self):
        super().__init__()
        self._set_feature("height_map", "C|V3")

    @staticmethod
    def minor_is_valid(key: int):
        return 1503 <= key < 1908


export = Anvil1503Interface
