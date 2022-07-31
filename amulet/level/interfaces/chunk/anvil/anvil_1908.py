from __future__ import annotations

from .anvil_1901 import Anvil1901Interface as ParentInterface


class Anvil1908Interface(ParentInterface):
    """
    Changed height keys again again
    """

    def __init__(self):
        super().__init__()
        self._set_feature("height_map", "C|V4")

    @staticmethod
    def minor_is_valid(key: int):
        return 1908 <= key < 1912


export = Anvil1908Interface
